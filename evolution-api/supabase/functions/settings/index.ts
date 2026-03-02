import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts'
import { createSupabaseClient } from '../_shared/supabaseClient.ts'

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createSupabaseClient(req)
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) throw new Error('Unauthorized')

    // GET /api/settings
    if (req.method === 'GET') {
      // maybeSingle é ideal aqui pois o usuário recém-criado pode ainda não ter settings armazenadas
      const { data, error } = await supabase.from('settings').select('*').eq('user_id', user.id).maybeSingle()
      if (error) throw error
      return new Response(JSON.stringify(data || {}), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // POST ou PUT /api/settings
    if (req.method === 'PUT' || req.method === 'POST') {
      const body = await req.json()
      // O Upsert cria ou atualiza dependendo se já existe um UUID para este usuário (onConflict)
      const { data, error } = await supabase.from('settings').upsert({ ...body, user_id: user.id }, { onConflict: 'user_id' }).select().single()
      if (error) throw error
      return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    throw new Error('Method not allowed')
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})

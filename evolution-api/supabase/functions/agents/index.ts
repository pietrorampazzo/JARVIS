import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts'
import { createSupabaseClient } from '../_shared/supabaseClient.ts'

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createSupabaseClient(req)
    // Valida autenticação do JWT via Header na lib do Supabase
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) throw new Error('Unauthorized')

    const url = new URL(req.url)
    const segments = url.pathname.split('/').filter(Boolean)
    // Ex: /agents/123-uuid -> segments[1] == '123-uuid'
    const agentId = segments.length > 1 ? segments[segments.length - 1] : null

    // GET /api/agents ou /api/agents/:id
    if (req.method === 'GET') {
      if (agentId && agentId !== 'agents') {
        const { data, error } = await supabase.from('agents').select('*').eq('id', agentId).single()
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      } else {
        const { data, error } = await supabase.from('agents').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }
    }

    // POST /api/agents
    if (req.method === 'POST') {
      const body = await req.json()
      // Força a inserção para o próprio usuário autenticado
      const { data, error } = await supabase.from('agents').insert({ ...body, user_id: user.id }).select().single()
      if (error) throw error
      return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // PUT /api/agents/:id
    if (req.method === 'PUT') {
      const body = await req.json()
      const { data, error } = await supabase.from('agents').update(body).eq('id', agentId).eq('user_id', user.id).select().single()
      if (error) throw error
      return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // DELETE /api/agents/:id
    if (req.method === 'DELETE') {
      const { error } = await supabase.from('agents').delete().eq('id', agentId).eq('user_id', user.id)
      if (error) throw error
      return new Response(JSON.stringify({ message: 'Deleted successfully' }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    throw new Error('Method not allowed')
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})

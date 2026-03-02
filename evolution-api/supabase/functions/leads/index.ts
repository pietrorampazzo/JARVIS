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

    const url = new URL(req.url)
    const segments = url.pathname.split('/').filter(Boolean)
    // Extrai o último segmento da URL. Ex: /api/leads/uuid -> 'uuid'
    const lastSegment = segments[segments.length - 1]
    const leadId = (lastSegment === 'leads' || lastSegment === 'import' || lastSegment === 'bulk-action') ? null : lastSegment

    // GET /api/leads ou /api/leads/:id ou /api/leads/:id/messages
    if (req.method === 'GET') {
      if (lastSegment === 'messages' || lastSegment === 'activities') {
        const id = segments[segments.length - 2]
        const table = lastSegment === 'messages' ? 'messages' : 'activity_logs'
        const { data, error } = await supabase.from(table).select('*').eq('lead_id', id).order('created_at', { ascending: false })
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      } else if (leadId) {
        // Exibição de um lead
        const { data, error } = await supabase.from('leads').select('*').eq('id', leadId).single()
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      } else {
        // Lista geral de leads com filtros
        const { searchParams } = url
        let query = supabase.from('leads').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
        
        if (searchParams.has('stage')) query = query.eq('stage', searchParams.get('stage'))
        if (searchParams.has('agent_id')) query = query.eq('agent_id', searchParams.get('agent_id'))
        
        const { data, error } = await query
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }
    }

    // POST /api/leads ou /api/leads/import
    if (req.method === 'POST') {
      if (lastSegment === 'import') {
        const { file_url, column_mapping, agent_id, tags } = await req.json()
        // Stub da Lógica de Importação (normalmente faria parse do CSV e batch insert)
        return new Response(JSON.stringify({ message: 'Import job created/scheduled', config: column_mapping }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }
      
      const body = await req.json()
      const { data, error } = await supabase.from('leads').insert({ ...body, user_id: user.id }).select().single()
      if (error) throw error
      return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // PUT /api/leads/:id ou /api/leads/:id/stage
    if (req.method === 'PUT') {
      if (lastSegment === 'stage') {
        const id = segments[segments.length - 2]
        const { stage } = await req.json()
        const { data, error } = await supabase.from('leads').update({ stage }).eq('id', id).eq('user_id', user.id).select().single()
        if (error) throw error
        return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      const body = await req.json()
      const { data, error } = await supabase.from('leads').update(body).eq('id', leadId).eq('user_id', user.id).select().single()
      if (error) throw error
      return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // DELETE /api/leads/:id
    if (req.method === 'DELETE') {
      const { error } = await supabase.from('leads').delete().eq('id', leadId).eq('user_id', user.id)
      if (error) throw error
      return new Response(JSON.stringify({ message: 'Deleted' }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    throw new Error('Method not allowed')
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})

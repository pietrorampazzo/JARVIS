import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

export const createSupabaseClient = (req: Request) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
  const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY') ?? ''
  
  // Cria cliente Supabase garantindo repasse do JWT do usuário via Authorization header 
  return createClient(supabaseUrl, supabaseAnonKey, {
    global: {
      headers: { Authorization: req.headers.get('Authorization')! },
    },
  })
}

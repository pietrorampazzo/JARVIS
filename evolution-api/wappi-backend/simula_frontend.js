import io from 'socket.io-client';

const socket = io('http://localhost:4000');

socket.on('connect', () => {
    console.log('✅ Cliente Simulado Conectado ao Gateway. ID:', socket.id);

    // 1. Simula entrada na sala do usuário (ex: um UUID qualquer de teste)
    const testUserId = 'user-frontend-123';
    socket.emit('join_room', { user_id: testUserId });

    // 2. Simula o evento Typing (Takeover do Frontend) para o Chat 'lead-test'
    console.log('⏳ Disparando "typing" takeover event...');
    socket.emit('typing', { user_id: testUserId, lead_id: 'lead-test' });
});

// Listener de eventos disparados Pelo Servidor pro Frontend
socket.on('new_message', (data) => {
    console.log('📩 Nova Mensagem Recebida via Socket:', data);
});

socket.on('notification', (data) => {
    console.log('🔔 Notificação do Sistema/Socket:', data);
});

socket.on('agent_status', (data) => {
    console.log('🤖 Mudança de Status do Agente:', data);
});

socket.on('connect_error', (error) => {
    console.error('❌ Erro de conexão Socket:', error.message);
});

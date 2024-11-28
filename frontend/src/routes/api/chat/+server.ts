import type { RequestHandler } from '@sveltejs/kit';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const { prompt } = await request.json();

        // Отправка запроса локальной модели (зависит от интерфейса модели)
        const response = await fetch('http://localhost:8000', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            return json({ reply: 'Ошибка связи с моделью' }, { status: 500 });
        }

        const data = await response.json();
        const generatedText = data.reply || 'Ответ не получен';

        return json({ reply: generatedText });
    } catch (error) {
        console.error('Ошибка:', error);
        return json({ reply: 'Произошла ошибка на сервере' }, { status: 500 });
    }
};
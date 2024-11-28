<script lang="ts">
	import "$lib/styles/chat-page.css";

	let inputPrompt: string = "";
	let chatHistory: { role: string; message: string }[] = [];
	let isChatStarted: boolean = false;

	// Отправка первого и последующих сообщений
	async function sendMessage() {
		if (inputPrompt.trim() === "") return;

		// Если чат еще не начался, переключаем состояние
		if (!isChatStarted) {
			isChatStarted = true;
			chatHistory = [
				{
					role: "assistant",
					message:
						"Здравствуйте, я ваш цифровой ассистент. Задавайте свой вопрос, и я найду на него ответ в загруженной базе знаний"
				}
			];
		}

		// Добавляем сообщение пользователя
		chatHistory = [...chatHistory, { role: "user", message: inputPrompt }];
		inputPrompt = "";

		// Имитация запроса к ИИ (замените на реальный API вызов)
		const response = await fetch("/api/chat", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ prompt: chatHistory[chatHistory.length - 1].message })
		});

		const data = await response.json();
		chatHistory = [...chatHistory, { role: "assistant", message: data.reply }];
	}
</script>

<div class="page-wrapper">
	<!-- Боковая панель -->
	<div class="side-panel">
		<!-- Здесь будет содержимое боковой панели -->
	</div>

	<!-- Окно с чатом -->
	{#if isChatStarted}
		<!-- История чата -->
		<div class="dialog">
			<div class="chat-history">
				{#each chatHistory as { role, message }}
					<div class="message {role}">
						<span>{message}</span>
					</div>
				{/each}
			</div>

			<!-- Поле ввода для последующих сообщений -->
			<div class="input-field">
				<img class="input-img" src="/icons/magnifier.png" alt="Иконка в форме лупы" />
				<input
					class="input-prompt"
					type="text"
					placeholder="Введите сообщение..."
					bind:value={inputPrompt}
					on:keydown={e => e.key === "Enter" && sendMessage()}
				/>
			</div>
		</div>
	{:else}
		<!-- Поле ввода для самого первого промпта  -->
		<div class="first-prompt">
			<span class="welcome-message">Чем я могу помочь?</span>
			<div class="first-input-field">
				<img class="input-img" src="/icons/magnifier.png" alt="Иконка в форме лупы" />
				<input
					class="input-prompt"
					type="text"
					placeholder="задайте вопрос"
					bind:value={inputPrompt}
					on:keydown={e => e.key === "Enter" && sendMessage()}
				/>
			</div>
		</div>
	{/if}
</div>

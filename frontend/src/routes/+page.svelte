<script lang="ts">
	import "$lib/styles/login-page.css";

	// Определяем типы для полей ввода
	let login: string = "";
	let password: string = "";
	let errorMessage: string = ""; // реактивная переменная для ошибки

	// Функция отправки формы с указанием типа события
	export async function handleSubmit(event: Event): Promise<void> {
		event.preventDefault();

		// Проверка логина и пароля
		if (login === "admin" && password === "1234") {
			errorMessage = ""; // очищаем строку с сообщением об ошибке
		} else {
			errorMessage = "Введён неверный логин или пароль";
		}
	}
</script>

<!-- Обёртка страницы -->
<div class="page-wrapper">
	<div class="container">
		<h1 class="main-heading">AI-assistant</h1>

		<!-- Обёртка формы -->
		<div class="form-wrapper">
			<span class="form-heading">Вход</span>

			<!-- Форма входа (для админа или суперпользователя) -->
			<form class="login-form" on:submit={handleSubmit} method="post">
				<label class="input-label">
					<span class="input-title">Логин</span>
					<input
						required
						class="input-item"
						type="text"
						bind:value={login}
						placeholder="Введите ваш логин"
					/>
				</label>

				<label class="input-label">
					<span class="input-title">Пароль</span>
					<input
						required
						class="input-item"
						type="password"
						bind:value={password}
						placeholder="Введите ваш пароль"
					/>
				</label>

				<!-- Кнопка отправления формы -->
				<button class="submit-button" type="submit">Войти</button>
			</form>

			<!-- Ссылка пока никуда не ведёт (страницы с чатом для гостей пока нет) -->
			<a class="guest-login" href="#">Войти как гость</a>
		</div>

		<!-- Если введён неверный логин или пароль, отображается сообщение об ошибке -->
		{#if errorMessage}
			<div class="auth-error">{errorMessage}</div>
		{/if}
	</div>
</div>
<!-- Форма входа (для админа или суперпользователя) -->
<form class="login-form" action="" method="post">
	<label class="input-label">
		<span class="input-title">Логин</span>
		<input required class="input-item" type="text" placeholder="Введите ваш логин" />
	</label>

	<label class="input-label">
		<span class="input-title">Пароль</span>
		<input required class="input-item" type="password" placeholder="Введите ваш пароль" />
	</label>

    <!-- Кнопка отправления формы -->
	<button class="submit-button" type="submit">Войти</button>
</form>

<style lang="css">
    /* Форма */
	.login-form {
		width: 400px;
		height: 228px;

		padding: 28px;

		border: 2px solid #2b27371a;
		border-radius: 25px;

		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

    /* Поля ввода */
	.input-label {
		width: 400px;
		height: 70px;

		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
	.input-title {
		font-size: 12px;
		font-weight: 400;
		line-height: 16px;
		color: #2b2737;
	}
	.input-item {
		padding: 9px 12px;

		border: none;
		border-radius: 12px;

		background-color: #fafafa;

		line-height: 24px;
	}
	.input-item::placeholder {
		font-size: 16px;
		font-weight: 400px;
		color: #11181c80;
	}

    /* Кнопка отправлени формы */
	.submit-button {
		padding: 12px 176.5px;

		font-size: 16px;
		font-weight: 400;
		line-height: 24px;

		border: none;
		border-radius: 12px;

		color: #ffffff;
		background-color: #2f56de;
	}
</style>

<script lang="js">
    // Подключение компонента LoginForm
    import LoginForm from "$lib/components/LoginForm.svelte";
</script>

<!-- Обёртка страницы -->
<div class="page-wrapper">
    <h1 class="main-heading">AI-assistant</h1>

    <!-- Обёртка формы -->
	<div class="form-wrapper">
        <span class="form-heading">Вход</span>

        <!-- Компонент LoginForm (форма входа) -->
        <LoginForm />

        <!-- Ссылка пока никуда не ведёт (страницы с чатом для гостей пока нет) -->
		<a class="guest-login" href="#">Войти как гость</a>
	</div>
</div>

<style lang="css">
    /* Обёртка страницы*/
	.page-wrapper {
        height: 100vh;
		background-color: #ffffff;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        row-gap: 47px;
	}

    /* Выравнивание заголовков по центру блока */
    .main-heading,
    .guest-login {
        text-align: center;
    }

    /* Обёртка формы */
    .form-wrapper {
        width: 456px;
        height: 371px;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Стили текста */
	.main-heading {
		font-size: 50px;
		font-weight: 400;
		line-height: 72px;
        color: #155EF2;
	}

    .form-heading {
        position: relative;
        left: 13px;

        font-size: 18px;
        font-weight: 600;
        line-height: 24px;
    }

    
	.guest-login {
        font-size: 14px;
        font-weight: 400;
        line-height: 24px;
		color: #2b273780;
		text-decoration: none;
	}
</style>

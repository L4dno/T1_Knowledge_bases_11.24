<script>
	import { dev } from "$app/environment";
	let selectedFiles = null;

	const handleFileUpload = event => {
		selectedFiles = event.target.files;
	};

	const uploadFiles = async () => {
		if (!selectedFiles) {
			alert("Добавьте документ для обновления базы знаний");
			return;
		}

		const formData = new FormData();
		for (let i = 0; i < selectedFiles.length; i++) {
			formData.append("files", selectedFiles[i]);
		}

		try {
			const response = await fetch("https://your-server-endpoint/upload", {
				method: "POST",
				body: formData
			});

			if (response.ok) {
				alert("Файлы успешно загружены!");
			} else {
				alert("Ошибка при загрузке файлов.");
			}
		} catch (error) {
			console.error("Ошибка:", error);
			alert("Ошибка при загрузке файлов.");
		}
	};

	// панель
	let open = false;

	const files = [
		{ name: "text.txt", type: "txt" },
		{ name: "file.xlsx", type: "xlsx" },
		{ name: "file.pdf", type: "pdf" },
		{ name: "https://www.st", type: "url" }
	];
</script>

<main>
	<div class="panel">
		<p class="txt_main">AI-assistant</p>
		<!-- каталог -->

		<div class="catalog">
			<button class="new_bz">Обновление БЗ</button>
			<div class="title" on:click={() => (open = !open)}>
				Мои документы
				<span class="arrow">{open ? "↑" : "↓"}</span>
			</div>

			{#if open}
				<ul class="files">
					{#each files as file}
						<li class="file">
							<span class="file-name">{file.name}</span>
						</li>
					{/each}
				</ul>
			{/if}

			<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br
			/><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
			<div>
				<button class="admin">Добавить админа</button>
			</div>
			<br />
			<div>
				<button class="exit">➜Выход</button>
			</div>
		</div>
	</div>
	<div class="main_button">
		<div>
			<!-- Скрытый input для выбора файлов -->
			<input type="file" multiple on:change={handleFileUpload} class="file-input" id="file-input" />
			<label for="file-input" class="upload-button">Выбрать файлы</label>
		</div>
	</div>
</main>

<style>
	@import url("https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Istok+Web:ital,wght@0,400;0,700;1,400;1,700&family=Oswald:wght@200..700&family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap");

	main {
		display: flex;
		width: auto;
		height: 1800px;
		background-color: #f1f5f9;
	}

	.main_button {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	/* панель */
	.panel {
		width: 450px;
		background-color: #fff;
		display: grid;
		justify-self: center;
	}

	.txt_main {
		font-size: 40px;
		display: grid;
		justify-self: center;
		color: #155ef2;
	}

	/* Скрываем стандартный input */
	.file-input {
		display: none;
	}

	/* Стили для метки, которая выглядит как кнопка */
	.upload-button {
		display: grid;
		justify-content: center;
		align-items: center;

		margin: 40px;
		padding: 10px;
		color: white;
		border-style: dashed;
		border-color: #2f56de80;
		border-radius: 24px;
		cursor: pointer;
		margin-bottom: 1em;
		color: #2f56de80;
		width: 934px;
		height: 200px;
		font-size: 40px;
		font-weight: 500;
	}

	.upload-button:hover {
		background-color: #58bcff;
	}

	.catalog {
		margin: -800px 90px;
		font-size: 30px;
		color: #2b273780;
	}

	.new_bz {
		height: 50px;
		width: 240px;
		border: none;
		background-color: #fff;
		font-size: 30px;
		font-weight: 500;
		margin: 10px;
	}

	.new_bz:hover {
		background-color: #797c81;
	}

	.admin {
		height: 50px;
		width: 300px;
		border: none;
		background-color: #fff;
		font-size: 30px;
		font-weight: 500;
		margin: -5px;
	}

	.admin:hover {
		background-color: #797c81;
	}

	.exit {
		height: 50px;
		width: 300px;
		border: none;
		background-color: #fff;
		font-size: 30px;
		font-weight: 500;
	}

	.exit:hover {
		background-color: #797c81;
	}
</style>

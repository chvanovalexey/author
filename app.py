import streamlit as st
import datetime
from config import (
    APP_TITLE,
    MODELS,
    RATE_LIMITS,
    DEFAULT_TEMPERATURE
)
from utils import (
    SYSTEM_PROMPT, 
    count_tokens, 
    estimate_cost, 
    generate_script,
    load_scripts, 
    save_scripts,
    load_script_versions,
    save_script_versions,
    create_message_from_context,
    get_context_parts,
    estimate_output_tokens
)

# Включаем wide mode для Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "scripts_data" not in st.session_state:
    st.session_state.scripts_data = load_scripts()

if "current_script" not in st.session_state:
    st.session_state.current_script = None

if "script_versions" not in st.session_state:
    st.session_state.script_versions = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# App title and description
st.title(APP_TITLE)
#st.subheader(APP_DESCRIPTION)

# Sidebar for navigation and script selection
with st.sidebar:
    # Добавляем expander для настройки температуры как первый элемент сайдбара
    with st.expander("Настройки LLM"):
        default_temperature = st.slider(
            "Температура по умолчанию", 
            min_value=0.0, 
            max_value=1.0, 
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            help="Более высокие значения делают результат более случайным, более низкие значения делают его более целенаправленным и детерминированным"
        )
        
        # Добавляем редактируемый системный промпт
        system_prompt = st.text_area(
            "Системный промпт",
            value=SYSTEM_PROMPT,
            height=200,
            help="Установите системный промпт для AI, который определяет его роль и стиль генерации"
        )
    
    st.header("Сценарии")
    
    # Create new script button
    if st.button("Создать новый сценарий"):
        st.session_state.current_script = {
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "title": "Новый сценарий",
            "brief": "",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.script_versions = []
        st.experimental_rerun()
        
    # List of existing scripts
    if st.session_state.scripts_data["scripts"]:
        st.subheader("Ваши сценарии")
        for script in st.session_state.scripts_data["scripts"]:
            if st.button(f"{script['title']} ({script['created_at']})", key=f"btn_{script['id']}"):
                st.session_state.current_script = script
                
                # Load script versions
                st.session_state.script_versions = load_script_versions(script['id'])
                
                # Присваиваем номера версиям, если у них еще нет номеров
                for i, version in enumerate(st.session_state.script_versions):
                    if 'version_number' not in version:
                        version['version_number'] = i + 1
                
                st.experimental_rerun()

# Main content area
if st.session_state.current_script:
    script = st.session_state.current_script
    
    # Script details section
    st.header("Детали сценария")
    
    # Title and brief summary inputs
    col1, col2 = st.columns([1, 3])
    
    with col1:
        new_title = st.text_input("Название сценария", script["title"])
    
    with col2:
        new_brief = st.text_area("Краткое описание", script["brief"], height=150, 
                              placeholder="Введите краткое описание вашей аудиоистории здесь...")
    
    # Update script if changed
    if new_title != script["title"] or new_brief != script["brief"]:
        script["title"] = new_title
        script["brief"] = new_brief
        script["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to session state
        found = False
        for i, s in enumerate(st.session_state.scripts_data["scripts"]):
            if s["id"] == script["id"]:
                st.session_state.scripts_data["scripts"][i] = script
                found = True
                break
        
        if not found:
            st.session_state.scripts_data["scripts"].append(script)
            
        # Save to disk
        save_scripts(st.session_state.scripts_data)
    
    # Generate script section
    st.header("Создать версию сценария")
    
    # Model selection with info
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Установить gpt-4o-mini как модель по умолчанию
        default_model_index = list(MODELS.keys()).index("gpt-4o-mini") if "gpt-4o-mini" in MODELS else 0
        selected_model = st.selectbox("Выберите AI модель", list(MODELS.keys()), index=default_model_index)
    
    with col2:
        st.markdown(f"**Качество**: {MODELS[selected_model]['quality']}/100")
    
    with col3:
        # Добавляем настройку температуры для текущей генерации
        temperature = st.slider(
            "Температура", 
            min_value=0.0, 
            max_value=1.0, 
            value=default_temperature,
            step=0.1
        )
    
    # Show model information
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
        <small>
            <b>Информация о модели:</b> Размер контекста: {format(MODELS[selected_model]['context_window'], ',')} токенов |
            Стоимость ввода: ${MODELS[selected_model]['input_cost']}/М токенов |
            Стоимость вывода: ${MODELS[selected_model]['output_cost']}/М токенов
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Rate limits information
    if selected_model in RATE_LIMITS:
        with st.expander("Информация о лимитах"):
            limits = RATE_LIMITS[selected_model]
            tpm = f"{limits.get('TPM', 'N/A'):,}" if isinstance(limits.get('TPM'), int) else limits.get('TPM', 'N/A')
            rpm = f"{limits.get('RPM', 'N/A'):,}" if isinstance(limits.get('RPM'), int) else limits.get('RPM', 'N/A')
            tpd = f"{limits.get('TPD', 'N/A'):,}" if isinstance(limits.get('TPD'), int) else limits.get('TPD', 'N/A')
            rpd = f"{limits.get('RPD', 'N/A'):,}" if isinstance(limits.get('RPD'), int) else limits.get('RPD', 'N/A')
            
            st.markdown(f"""
            - **Токенов в минуту (TPM)**: {tpm}
            - **Запросов в минуту (RPM)**: {rpm}
            - **Токенов в день (TPD)**: {tpd}
            - **Запросов в день (RPD)**: {rpd}
            """)
    
    # Context selection for regeneration
    include_brief = True  # Always include brief
    
    # Include previous versions if they exist
    selected_versions = []
    if st.session_state.script_versions:
        with st.expander("Включить предыдущие версии в контекст"):
            if st.session_state.script_versions:
                # Стиль для таблицы
                st.markdown("""
                <style>
                .version-table {
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-size: 0.9em;
                    width: 100%;
                }
                .version-table th {
                    background-color: #f0f2f6;
                    color: #262730;
                    font-weight: bold;
                    text-align: left;
                    padding: 8px;
                }
                .version-table td {
                    padding: 8px;
                    border-bottom: 1px solid #e1e4e8;
                }
                /* Стили для более компактной таблицы */
                .st-emotion-cache-1v0mbdj > div {
                    margin-top: 0 !important;
                    margin-bottom: 0 !important;
                    padding-top: 2px !important;
                    padding-bottom: 2px !important;
                }
                /* Уменьшаем отступы в markdown */
                .st-emotion-cache-1v0mbdj p {
                    margin-top: 0 !important;
                    margin-bottom: 0 !important;
                    line-height: 1.2 !important;
                }
                /* Компактные строки в нашей кастомной таблице */
                div[style*="background-color"] {
                    padding-top: 0px !important;
                    padding-bottom: 0px !important;
                    margin-top: 0px !important;
                    margin-bottom: 0px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Create a custom table-like interface with checkboxes
                st.markdown("<p style='margin: 0 0 5px 0; font-size: 0.9em;'>Выберите версии для включения в контекст:</p>", unsafe_allow_html=True)
                
                # Header row
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 1.5, 1, 1, 1, 1])
                with col1:
                    st.markdown("<small><strong>#</strong></small>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<small><strong>Дата</strong></small>", unsafe_allow_html=True)
                with col3:
                    st.markdown("<small><strong>Модель</strong></small>", unsafe_allow_html=True)
                with col4:
                    st.markdown("<small><strong>Размер</strong></small>", unsafe_allow_html=True)
                with col5:
                    st.markdown("<small><strong>Токены</strong></small>", unsafe_allow_html=True)
                with col6:
                    st.markdown("<small><strong>✓</strong></small>", unsafe_allow_html=True)
                
                # Divider - делаем тонкую линию
                st.markdown('<hr style="margin: 0; padding: 0; height: 1px; border: none; background-color: #e1e4e8;">', unsafe_allow_html=True)
                
                # Data rows
                for i, version in enumerate(st.session_state.script_versions):
                    timestamp = version.get('timestamp', 'No date')
                    model = version.get('model', 'Unknown')
                    content_length = len(version.get('content', ''))
                    tokens = version.get('input_tokens', 0)
                    cost = version.get('estimated_cost', 0)
                    
                    # Row with alternating background color
                    bg_color = "#f8f9fa" if i % 2 == 0 else "white"
                    st.markdown(f'<div style="background-color: {bg_color}; padding: 1px 0;">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 1.5, 1, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"<small>**{i+1}**</small>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<small>{timestamp}</small>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<small>{model}</small>", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"<small>{content_length//100}00 симв.</small>", unsafe_allow_html=True)
                    with col5:
                        st.markdown(f"<small>{format(tokens, ',')}</small>", unsafe_allow_html=True)
                    with col6:
                        if st.checkbox("", key=f"v_{i}"):
                            # Добавляем номер версии в объект версии перед добавлением в список выбранных
                            version_with_number = version.copy()
                            version_with_number['version_number'] = i+1  # Сохраняем фактический номер версии
                            selected_versions.append(version_with_number)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # User prompt input
    user_prompt = st.text_area("Опишите, что вы хотите в этой версии сценария", height=100, 
                          placeholder="Например: 'Сделайте его более драматичным, с напряженными музыкальными акцентами и четкими различиями между персонажами'")
    
    # Token counting and cost estimation
    if user_prompt:
        # Create messages and context parts for display
        messages = create_message_from_context(system_prompt, script['brief'], selected_versions, user_prompt)
        context_parts = get_context_parts(script['brief'], selected_versions, user_prompt)
        
        # Count tokens and estimate cost
        full_prompt = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens(full_prompt, selected_model)
        
        # Estimate output tokens based on brief length
        estimated_output_tokens = estimate_output_tokens(len(script["brief"]))
        
        # Calculate cost
        estimated_cost = estimate_cost(input_tokens, estimated_output_tokens, selected_model)
        
        # Display token info and cost in a metrics container
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Входные токены", format(input_tokens, ','), f"Осталось {format(MODELS[selected_model]['context_window'] - input_tokens, ',')}")
        
        with col2:
            st.metric("Оценка выходных токенов", format(estimated_output_tokens, ','))
        
        with col3:
            st.metric("Оценка стоимости", f"${estimated_cost:.4f}")
        
        # Warning if exceeding context window
        if input_tokens > MODELS[selected_model]["context_window"]:
            st.error(f"⚠️ Ввод превышает размер контекста модели в {format(MODELS[selected_model]['context_window'], ',')} токенов. Пожалуйста, уменьшите контекст.")
        
        # Show context parts
        with st.expander("Просмотр компонентов контекста"):
            for part in context_parts:
                st.subheader(part["type"])
                st.text_area(f"Содержимое {part['type']}", part["content"][:500] + ("..." if len(part["content"]) > 500 else ""), height=100, disabled=True)
                st.text(f"Токенов: {format(count_tokens(part['content'], selected_model), ',')}")
                st.divider()
        
        # Generate button
        if st.button("Создать сценарий", type="primary", disabled=input_tokens > MODELS[selected_model]["context_window"]):
            if input_tokens <= MODELS[selected_model]["context_window"]:
                with st.spinner("Создание сценария... Это может занять минуту."):
                    try:
                        # Передаем значение температуры в функцию generate_script
                        generated_script = generate_script(messages, selected_model, temperature)
                        
                        # Save the new version
                        new_version = {
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "model": selected_model,
                            "temperature": temperature,
                            "prompt": user_prompt,
                            "content": generated_script,
                            "input_tokens": input_tokens,
                            "estimated_cost": estimated_cost,
                            "context": [p["type"] for p in context_parts],
                            "version_number": len(st.session_state.script_versions) + 1  # Присваиваем номер версии
                        }
                        
                        st.session_state.script_versions.append(new_version)
                        
                        # Save versions to disk
                        save_script_versions(script['id'], st.session_state.script_versions)
                        
                        # Устанавливаем активную вкладку на последнюю (новую) версию
                        st.session_state.active_tab = len(st.session_state.script_versions) - 1
                        
                        st.success("Сценарий успешно создан!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Ошибка при создании сценария: {str(e)}")
            else:
                st.error("Невозможно создать сценарий: ввод превышает лимит токенов.")
    
    # View script versions
    if st.session_state.script_versions:
        st.header("Версии сценария")
        
        # Определяем CSS-стили для контейнера markdown один раз перед циклом
        st.markdown("""
        <style>
        .markdown-container {
            max-height: 400px; 
            overflow-y: auto; 
            border: 1px solid #e6e9ef; 
            border-radius: 0.25rem; 
            padding: 1rem; 
            background-color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab_titles = [f"Версия {i+1}" for i in range(len(st.session_state.script_versions))]
        tabs = st.tabs(tab_titles)
        
        # Используем значение active_tab из session_state для определения активной вкладки
        # Streamlit автоматически отобразит активную вкладку, нам нужно только установить индекс
        st.session_state.active_tab = min(st.session_state.active_tab, len(tabs) - 1)
        
        for i, (tab, version) in enumerate(zip(tabs, st.session_state.script_versions)):
            with tab:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Информация о создании")
                    # Добавляем информацию о температуре в вывод
                    temp_info = f" (Температура: {version.get('temperature', DEFAULT_TEMPERATURE)})" if 'temperature' in version else ""
                    st.markdown(f"""
                    - **Дата:** {version.get('timestamp', 'Нет даты')}
                    - **Модель:** {version.get('model', 'Неизвестно')}{temp_info}
                    - **Токенов:** {format(version.get('input_tokens', 0), ',')}
                    - **Стоимость:** ${version.get('estimated_cost', 0):.4f}
                    - **Использованный контекст:** {', '.join(version.get('context', ['Краткое описание']))}
                    """)
                
                with col2:
                    # Download button
                    timestamp = version.get("timestamp", "").replace(" ", "_").replace(":", "-")
                    download_filename = f"{script['title'].replace(' ', '_')}_{timestamp}.txt"
                    
                    st.download_button(
                        label="Скачать эту версию",
                        data=version.get("content", ""),
                        file_name=download_filename,
                        mime="text/plain",
                        key=f"download_{i}"
                    )
                
                st.subheader("Запрос для создания")
                st.info(version.get("prompt", "Запрос недоступен"))
                
                st.subheader("Созданный сценарий")
                
                # Получаем содержимое сценарий
                content = version.get("content", "Содержимое недоступно")
                
                # Открываем HTML-контейнер
                st.markdown('<div class="markdown-container">', unsafe_allow_html=True)
                
                # Отображаем содержимое как markdown (безопасно, с сохранением форматирования)
                st.markdown(content)
                
                # Закрываем HTML-контейнер
                st.markdown('</div>', unsafe_allow_html=True)

# Initial greeting if no script is selected
else:
    st.write("Добро пожаловать! Создайте новый сценарий или выберите существующий на боковой панели, чтобы начать.")
    
    st.markdown("""
    ## Как использовать это приложение
    
    1. **Создайте новый сценарий** с помощью кнопки на боковой панели
    2. **Введите краткое описание** вашей аудиоистории
    3. **Опишите, что вы хотите** в вашем сценарие
    4. **Создайте сценарий** с помощью AI модели
    5. **Улучшайте ваш сценарий** создавая новые версии с разными запросами
    6. **Скачайте финальный сценарий** когда будете удовлетворены результатом
    
    Приложение отслеживает все версии, так что вы можете свободно экспериментировать!
    """)
    
    # Feature overview
    st.subheader("Возможности")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🤖 С поддержкой ИИ")
        st.markdown("Использует мощные языковые модели OpenAI для создания высококачественных аудиосценариев")
    
    with col2:
        st.markdown("### 📝 Контроль версий")
        st.markdown("Отслеживайте все версии сценария и запросы, использованные для их создания")
    
    with col3:
        st.markdown("### 💰 Оценка стоимости")
        st.markdown("Оценивайте стоимость создания сценария перед отправкой запросов к API") 
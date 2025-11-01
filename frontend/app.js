// API конфигурация
// Определяем базовый URL API динамически на основе текущего хоста
const API_BASE_URL = (() => {
    // В продакшене используем относительный путь
    // В режиме разработки можно использовать полный URL
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://127.0.0.1:8000/api';
    }
    // Относительный путь работает везде
    return '/api';
})();

// Глобальные переменные
let categories = [];
let selectedCategory = null;
let searchTimeout = null;
let categoriesLoaded = false; // Флаг загрузки категорий

// Элементы DOM
const elements = {
    // Поиск категории
    categorySearch: document.getElementById('categorySearch'),
    categoryDropdown: document.getElementById('categoryDropdown'),
    categoryCommissions: document.getElementById('categoryCommissions'),
    fboCommission: document.getElementById('fboCommission'),
    fbsCommission: document.getElementById('fbsCommission'),
    
    // Параметры товара
    price: document.getElementById('price'),
    weight: document.getElementById('weight'),
    
    // Габариты/Объём
    dimensionsBtn: document.getElementById('dimensionsBtn'),
    volumeBtn: document.getElementById('volumeBtn'),
    dimensionsInputs: document.getElementById('dimensionsInputs'),
    volumeInputs: document.getElementById('volumeInputs'),
    length: document.getElementById('length'),
    width: document.getElementById('width'),
    height: document.getElementById('height'),
    volumeInput: document.getElementById('volumeInput'),
    calculatedVolume: document.getElementById('calculatedVolume'),
    
    // Расчёт прибыли
    showProfitFields: document.getElementById('showProfitFields'),
    profitFields: document.getElementById('profitFields'),
    taxRate: document.getElementById('taxRate'),
    buyoutRate: document.getElementById('buyoutRate'),
    deliveryTime: document.getElementById('deliveryTime'),
    costPrice: document.getElementById('costPrice'),
    otherCosts: document.getElementById('otherCosts'),
    monthlySales: document.getElementById('monthlySales'),
    adCosts: document.getElementById('adCosts'),
    
    // Кнопки
    calculateBtn: document.getElementById('calculateBtn'),
    resetBtn: document.getElementById('resetBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    
    // Результаты
    resultsTable: document.getElementById('resultsTable'),
    kpiTiles: document.getElementById('kpiTiles'),
    breakdowns: document.getElementById('breakdowns'),
    sensitivity: document.getElementById('sensitivity'),
    loadingSpinner: document.getElementById('loadingSpinner'),
    errorMessage: document.getElementById('errorMessage')
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    // Загружаем небольшую выборку категорий для быстрого старта
    loadCategories();
    setupEventListeners();
    updateCalculatedVolume();
});

// Загрузка первых N категорий (для первичного отображения)
async function loadCategories() {
    if (categoriesLoaded) return categories; // Уже загружены
    
    try {
        const response = await fetch(`${API_BASE_URL}/categories/?page_size=50`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        categories = data.results || [];
        if (categories.length > 0) {
            categoriesLoaded = true;
            console.log(`Загружено ${categories.length} категорий`);
        }
        return categories;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        // При ошибке сети пытаемся использовать относительный путь еще раз
        if (API_BASE_URL !== '/api') {
            try {
                const fallbackResponse = await fetch('/api/categories/?page_size=50');
                if (fallbackResponse.ok) {
                    const fallbackData = await fallbackResponse.json();
                    categories = fallbackData.results || [];
                    if (categories.length > 0) {
                        categoriesLoaded = true;
                        console.log(`Загружено ${categories.length} категорий (fallback)`);
                        return categories;
                    }
                }
            } catch (e) {
                console.error('Fallback также не сработал:', e);
            }
        }
        categoriesLoaded = false;
        return [];
    }
}

// Поиск категорий на сервере
async function searchCategoriesServer(query) {
    try {
        const url = `${API_BASE_URL}/categories/?search=${encodeURIComponent(query)}&page_size=20`;
        const response = await fetch(url);
        if (!response.ok) {
            // Пробуем fallback на относительный путь
            if (API_BASE_URL !== '/api') {
                const fallbackUrl = `/api/categories/?search=${encodeURIComponent(query)}&page_size=20`;
                const fallbackResponse = await fetch(fallbackUrl);
                if (fallbackResponse.ok) {
                    const fallbackData = await fallbackResponse.json();
                    return fallbackData.results || [];
                }
            }
            return [];
        }
        const data = await response.json();
        return data.results || [];
    } catch (e) {
        console.error('Ошибка поиска категорий:', e);
        // Пробуем fallback
        if (API_BASE_URL !== '/api') {
            try {
                const fallbackUrl = `/api/categories/?search=${encodeURIComponent(query)}&page_size=20`;
                const fallbackResponse = await fetch(fallbackUrl);
                if (fallbackResponse.ok) {
                    const fallbackData = await fallbackResponse.json();
                    return fallbackData.results || [];
                }
            } catch (e2) {
                console.error('Fallback поиска также не сработал:', e2);
            }
        }
        return [];
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Поиск категории
    elements.categorySearch.addEventListener('input', handleCategorySearch);
    // При фокусе на поле поиска сразу показываем категории
    elements.categorySearch.addEventListener('focus', async () => {
        if (!categoriesLoaded) {
            await loadCategories();
        }
        if (categories.length > 0 && elements.categorySearch.value.trim().length === 0) {
            displayCategories(categories);
        }
    });
    document.addEventListener('click', (e) => {
        if (!elements.categorySearch.contains(e.target) && !elements.categoryDropdown.contains(e.target)) {
            elements.categoryDropdown.classList.add('hidden');
        }
    });
    
    // Переключение Габариты/Объём
    elements.dimensionsBtn.addEventListener('click', () => switchMode('dimensions'));
    elements.volumeBtn.addEventListener('click', () => switchMode('volume'));
    
    // Обновление объёма при изменении габаритов
    elements.length.addEventListener('input', updateCalculatedVolume);
    elements.width.addEventListener('input', updateCalculatedVolume);
    elements.height.addEventListener('input', updateCalculatedVolume);
    
    // Показать/скрыть поля расчёта
    elements.showProfitFields.addEventListener('change', toggleProfitFields);
    
    // Кнопки
    elements.calculateBtn.addEventListener('click', calculate);
    elements.downloadBtn.addEventListener('click', downloadExcel);
    elements.resetBtn.addEventListener('click', resetForm);
    
    // Авто-выбор категории при старте отключен, чтобы не вводить пользователя в заблуждение
}

// Поиск категорий
async function handleCategorySearch() {
    const query = elements.categorySearch.value.trim();
    
    // Если категории еще не загружены, загружаем их при фокусе
    if (!categoriesLoaded && query.length === 0) {
        await loadCategories();
    }
    
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        if (query.length === 0) {
            // Если категории еще не загружены, загружаем их
            if (!categoriesLoaded) {
                await loadCategories();
            }
            // Показываем короткий список локально загруженных категорий
            if (categories.length > 0) {
                displayCategories(categories);
            } else {
                // Пытаемся загрузить еще раз
                await loadCategories();
                if (categories.length > 0) {
                    displayCategories(categories);
                } else {
                    elements.categoryDropdown.innerHTML = '<div class="category-item">Начните вводить название для поиска</div>';
                    elements.categoryDropdown.classList.remove('hidden');
                }
            }
            return;
        }
        const results = await searchCategoriesServer(query);
        // Кэшируем найденные категории для повторного выбора по id
        if (results.length > 0) {
            categories = results;
            displayCategories(results);
        } else {
            elements.categoryDropdown.innerHTML = '<div class="category-item">Категории не найдены</div>';
            elements.categoryDropdown.classList.remove('hidden');
        }
    }, 250);
}

// Показать все категории
function showAllCategories() {
    displayCategories(categories);
}

// Отобразить категории в dropdown
function displayCategories(cats) {
    if (cats.length === 0) {
        elements.categoryDropdown.innerHTML = '<div class="category-item">Категории не найдены</div>';
        elements.categoryDropdown.classList.remove('hidden');
        return;
    }
    
    // Проверяем наличие дубликатов по названию типа товара
    const nameCounts = {};
    cats.forEach(cat => {
        nameCounts[cat.name] = (nameCounts[cat.name] || 0) + 1;
    });
    
    elements.categoryDropdown.innerHTML = cats.map(cat => {
        // Если есть дубликаты по названию - показываем категорию в скобках
        const displayName = (nameCounts[cat.name] > 1 && cat.category_group) 
            ? `${cat.name} <span style="color: #666;">(${cat.category_group})</span>`
            : cat.name;
        
        return `
            <div class="category-item" data-id="${cat.id}">
                ${displayName}
            </div>
        `;
    }).join('');
    
    elements.categoryDropdown.classList.remove('hidden');
    
    // Обработчики клика на категории
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', () => {
            const catId = parseInt(item.dataset.id);
            const category = categories.find(c => c.id === catId);
            if (category) {
                selectCategory(category);
            }
        });
    });
}

// Выбрать категорию
function selectCategory(category) {
    selectedCategory = category;
    // Показываем название с категорией, если она есть
    const displayName = category.category_group 
        ? `${category.name} (${category.category_group})`
        : category.name;
    elements.categorySearch.value = displayName;
    elements.fboCommission.textContent = category.fbo_commission;
    elements.fbsCommission.textContent = category.fbs_commission;
    elements.categoryCommissions.classList.remove('hidden');
    elements.categoryDropdown.classList.add('hidden');
}

// Переключение режима Габариты/Объём
function switchMode(mode) {
    if (mode === 'dimensions') {
        elements.dimensionsBtn.classList.add('active');
        elements.volumeBtn.classList.remove('active');
        elements.dimensionsInputs.classList.remove('hidden');
        elements.volumeInputs.classList.add('hidden');
        updateCalculatedVolume();
    } else {
        elements.volumeBtn.classList.add('active');
        elements.dimensionsBtn.classList.remove('active');
        elements.volumeInputs.classList.remove('hidden');
        elements.dimensionsInputs.classList.add('hidden');
    }
}

// Обновление рассчитанного объёма
function updateCalculatedVolume() {
    const length = parseFloat(elements.length.value) || 0;
    const width = parseFloat(elements.width.value) || 0;
    const height = parseFloat(elements.height.value) || 0;
    
    const volume = (length * width * height) / 1000;
    elements.calculatedVolume.textContent = volume.toFixed(3);
}

// Показать/скрыть поля расчёта
function toggleProfitFields() {
    if (elements.showProfitFields.checked) {
        elements.profitFields.classList.remove('hidden');
    } else {
        elements.profitFields.classList.add('hidden');
    }
}

// Получить выбранную ставку налога
function getSelectedTaxRate() {
    return parseFloat(elements.taxRate.value) || 6;
}

function buildRequestPayload() {
    if (!selectedCategory) {
        throw new Error('Пожалуйста, выберите категорию товара');
    }

    const isDimensionsMode = elements.dimensionsBtn.classList.contains('active');
    const payload = {
        category_id: selectedCategory.id,
        price: parseFloat(elements.price.value) || 0,
        weight: parseFloat(elements.weight.value) || 0,
        dimension_mode: isDimensionsMode ? 'dimensions' : 'volume',
        tax_rate: getSelectedTaxRate(),
        buyout_rate: parseFloat(elements.buyoutRate.value) || 0,
        delivery_time: parseInt(elements.deliveryTime.value) || 1,
        ad_costs_rate: parseFloat(elements.adCosts.value) || 0,
        cost_price: parseFloat(elements.costPrice.value) || 0,
        other_costs: parseFloat(elements.otherCosts.value) || 0,
        monthly_sales: parseInt(elements.monthlySales.value) || 1
    };

    if (isDimensionsMode) {
        payload.length = parseFloat(elements.length.value) || 0;
        payload.width = parseFloat(elements.width.value) || 0;
        payload.height = parseFloat(elements.height.value) || 0;
    } else {
        payload.volume = parseFloat(elements.volumeInput.value) || 0;
    }

    return payload;
}

// Расчёт
async function calculate() {
    let data;
    try {
        data = buildRequestPayload();
    } catch (error) {
        showError(error.message);
        return;
    }
    
    // Показать загрузку
    elements.loadingSpinner.classList.remove('hidden');
    elements.errorMessage.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Ошибка при расчёте');
        }
        
        const results = await response.json();
        displayResults(results);
        displayKpi(results);
        displayBreakdowns(results);
        displaySensitivity(results);
    } catch (error) {
        showError(error.message);
    } finally {
        elements.loadingSpinner.classList.add('hidden');
    }
}

async function downloadExcel() {
    let data;
    try {
        data = buildRequestPayload();
    } catch (error) {
        showError(error.message);
        return;
    }

    elements.errorMessage.classList.add('hidden');
    elements.downloadBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/calculate/export/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Не удалось сформировать файл');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        const safeName = selectedCategory ? selectedCategory.name.replace(/[^\w\d-]+/g, '_') : 'ozon_calc';
        const timestamp = new Date().toISOString().replace(/[-:T]/g, '').split('.')[0];
        link.href = url;
        link.download = `${safeName}_${timestamp}.xlsx`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError(error.message);
    } finally {
        elements.downloadBtn.disabled = false;
    }
}

// Отображение результатов
function displayResults(results) {
    const { fbo_results, fbs_results } = results;
    const monthlySales = parseInt(elements.monthlySales.value) || 1000;
    
    // Доли для многоцветного бара (в процентах от цены)
    const fboBlue = Math.abs(parseFloat(fbo_results.total_ozon_costs_percent));
    const fboGray = Math.abs(parseFloat(fbo_results.cost_price_percent)) + Math.abs(parseFloat(fbo_results.profit_tax_percent)) + Math.abs(parseFloat(fbo_results.other_costs_percent));
    const fboGreen = Math.max(0, 100 - (fboBlue + fboGray));
    
    const fbsBlue = Math.abs(parseFloat(fbs_results.total_ozon_costs_percent));
    const fbsGray = Math.abs(parseFloat(fbs_results.cost_price_percent)) + Math.abs(parseFloat(fbs_results.profit_tax_percent)) + Math.abs(parseFloat(fbs_results.other_costs_percent));
    const fbsGreen = Math.max(0, 100 - (fbsBlue + fbsGray));
    
    const html = `
        <div class="table-header">
            <div></div>
            <div>FBO</div>
            <div>FBS</div>
        </div>
        
        ${createPriceRow('Цена товара', fbo_results, fbs_results, { fboBlue, fboGray, fboGreen, fbsBlue, fbsGray, fbsGreen })}
        ${createOffsetRow('Вознаграждение Ozon', fbo_results.ozon_reward, fbs_results.ozon_reward, fbo_results.ozon_reward_percent, fbs_results.ozon_reward_percent, 0, 0, 'seg-blue')}
        ${createOffsetRow('Эквайринг', fbo_results.acquiring, fbs_results.acquiring, fbo_results.acquiring_percent, fbs_results.acquiring_percent, fbo_results.ozon_reward_percent, fbs_results.ozon_reward_percent, 'seg-blue')}
        ${createOffsetRow('Обработка и доставка', fbo_results.processing_delivery, fbs_results.processing_delivery, fbo_results.processing_delivery_percent, fbs_results.processing_delivery_percent, (parseFloat(fbo_results.ozon_reward_percent)+parseFloat(fbo_results.acquiring_percent)), (parseFloat(fbs_results.ozon_reward_percent)+parseFloat(fbs_results.acquiring_percent)), 'seg-blue', true)}
        ${createOffsetRow('Возвраты и отмены', fbo_results.returns_cancellations, fbs_results.returns_cancellations, fbo_results.returns_cancellations_percent, fbs_results.returns_cancellations_percent, (parseFloat(fbo_results.ozon_reward_percent)+parseFloat(fbo_results.acquiring_percent)+parseFloat(fbo_results.processing_delivery_percent)), (parseFloat(fbs_results.ozon_reward_percent)+parseFloat(fbs_results.acquiring_percent)+parseFloat(fbs_results.processing_delivery_percent)), 'seg-blue', true)}
        ${createRow('Затраты на Ozon за шт', fbo_results.total_ozon_costs, fbs_results.total_ozon_costs, fbo_results.total_ozon_costs_percent, fbs_results.total_ozon_costs_percent, 'negative', false, true)}
        ${createOffsetRow('Себестоимость товара', fbo_results.cost_price, fbs_results.cost_price, fbo_results.cost_price_percent, fbs_results.cost_price_percent, fboBlue, fbsBlue, 'seg-gray')}
        ${createOffsetRow('Налог на прибыль', fbo_results.profit_tax, fbs_results.profit_tax, fbo_results.profit_tax_percent, fbs_results.profit_tax_percent, (fboBlue+parseFloat(fbo_results.cost_price_percent)), (fbsBlue+parseFloat(fbs_results.cost_price_percent)), 'seg-gray')}
        ${createOffsetRow('Прочие затраты', fbo_results.other_costs, fbs_results.other_costs, fbo_results.other_costs_percent, fbs_results.other_costs_percent, (fboBlue+parseFloat(fbo_results.cost_price_percent)+parseFloat(fbo_results.profit_tax_percent)), (fbsBlue+parseFloat(fbs_results.cost_price_percent)+parseFloat(fbs_results.profit_tax_percent)), 'seg-gray')}
        ${createOffsetRow('Прибыль за шт', fbo_results.net_profit_per_unit, fbs_results.net_profit_per_unit, fbo_results.net_profit_per_unit_percent, fbs_results.net_profit_per_unit_percent, (fboBlue+fboGray), (fbsBlue+fbsGray), 'seg-green', false, true)}
        ${createTotalRow(`Прибыль за ${monthlySales} шт`, fbo_results.net_profit_total, fbs_results.net_profit_total)}
    `;
    
    elements.resultsTable.innerHTML = html;
    elements.resultsTable.classList.remove('hidden');
}

function displayKpi(results) {
    const { fbo_results, fbs_results } = results;
    elements.kpiTiles.innerHTML = `
        <div class="kpi-tile">
            <div class="kpi-title">Прибыль за шт</div>
            <div class="kpi-value">FBO: ${formatNumber(fbo_results.net_profit_per_unit)} ₽ | FBS: ${formatNumber(fbs_results.net_profit_per_unit)} ₽</div>
        </div>
        <div class="kpi-tile">
            <div class="kpi-title">Маржа, %</div>
            <div class="kpi-value">FBO: ${formatPercent(fbo_results.net_profit_per_unit_percent)}% | FBS: ${formatPercent(fbs_results.net_profit_per_unit_percent)}%</div>
        </div>
        <div class="kpi-tile">
            <div class="kpi-title">Прибыль/мес → год</div>
            <div class="kpi-value">FBO: ${formatNumber(fbo_results.net_profit_total)} / ${formatNumber(fbo_results.annual_net_profit)} ₽</div>
        </div>
    `;
    elements.kpiTiles.classList.remove('hidden');
}

function displayBreakdowns(results) {
    const { fbo_results, fbs_results } = results;
    const f = (fbo_results && fbo_results.logistics_breakdown) || { base: 0, time_coeff: 0, price_percent_component: 0 };
    const r = (fbo_results && fbo_results.returns_breakdown) || { base: 0, not_buyout_share: 0 };
    elements.breakdowns.innerHTML = `
        <div class="block-title">Декомпозиция FBO</div>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-title">Логистика</div>
                <div class="metric-value">${formatNumber(f.base)} ₽</div>
                <div class="metric-caption">Базовый тариф</div>
                <div class="metric-list">
                    <div class="metric-row"><span>Коэфф. времени</span><span>${formatNumber(f.time_coeff)}</span></div>
                    <div class="metric-row"><span>Надбавка от цены</span><span>${formatNumber(f.price_percent_component)} ₽</span></div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Возвраты</div>
                <div class="metric-value">${formatNumber(r.base)} ₽</div>
                <div class="metric-caption">Оплачиваемая обратная логистика</div>
                <div class="metric-list">
                    <div class="metric-row"><span>Доля невыкупа</span><span>${formatPercent(r.not_buyout_share*100)}%</span></div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Эффективные проценты</div>
                <div class="metric-value">${formatPercent(fbo_results.effective_ozon_fee_percent)}%</div>
                <div class="metric-caption">Сумма комиссий и логистики</div>
                <div class="metric-list">
                    <div class="metric-row"><span>Валовая до налога</span><span>${formatPercent(fbo_results.gross_margin_before_tax_percent)}%</span></div>
                    <div class="metric-row"><span>Профит до расходов</span><span>${formatNumber(fbo_results.profit_before_costs)} ₽</span></div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Точки цены</div>
                <div class="metric-value">${formatNumber(fbo_results.break_even_price)} ₽</div>
                <div class="metric-caption">Безубыточность</div>
                <div class="metric-list">
                    <div class="metric-row"><span>Маржа 10%</span><span>${formatNumber(fbo_results.target_price_10pct)} ₽</span></div>
                    <div class="metric-row"><span>Маржа 20%</span><span>${formatNumber(fbo_results.target_price_20pct)} ₽</span></div>
                </div>
            </div>
        </div>
    `;
    elements.breakdowns.classList.remove('hidden');
}

function displaySensitivity(results) {
    const s = results && results.fbo_results && results.fbo_results.sensitivity;
    // Если чувствительность отсутствует или некорректна — скрываем блок и выходим без ошибок
    if (!s || !Array.isArray(s.price) || !Array.isArray(s.buyout) || !Array.isArray(s.delivery_time)) {
        elements.sensitivity.classList.add('hidden');
        elements.sensitivity.innerHTML = '';
        return;
    }

    const priceRows = s.price.map(p => `
        <tr>
            <td>${p.delta_pct}%</td>
            <td class="num">${formatNumber(p.price)} ₽</td>
            <td class="num">${formatNumber(p.net_profit_per_unit)} ₽</td>
            <td class="num">${formatPercent(p.net_profit_per_unit_percent)}%</td>
        </tr>
    `).join('');
    const buyoutRows = s.buyout.map(p => `
        <tr>
            <td>${p.buyout_rate}%</td>
            <td class="num">${formatNumber(p.net_profit_per_unit)} ₽</td>
            <td class="num">${formatPercent(p.net_profit_per_unit_percent)}%</td>
        </tr>
    `).join('');
    const delivRows = s.delivery_time.map(p => `
        <tr>
            <td>${p.hours} ч</td>
            <td class="num">${formatNumber(p.net_profit_per_unit)} ₽</td>
            <td class="num">${formatPercent(p.net_profit_per_unit_percent)}%</td>
        </tr>
    `).join('');
    elements.sensitivity.innerHTML = `
        <div class="block-title">Чувствительность (FBO)</div>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-title">Цена</div>
                <div class="metric-caption">Как меняется прибыль при колебаниях цены</div>
                <div class="metric-table-wrapper">
                    <table class="metric-table">
                        <thead>
                            <tr><th>Δ%</th><th class="num">Цена</th><th class="num">Прибыль/шт</th><th class="num">%</th></tr>
                        </thead>
                        <tbody>${priceRows}</tbody>
                    </table>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Выкуп</div>
                <div class="metric-caption">Влияние доли выкупа на прибыль</div>
                <div class="metric-table-wrapper">
                    <table class="metric-table">
                        <thead>
                            <tr><th>Выкуп</th><th class="num">Прибыль/шт</th><th class="num">%</th></tr>
                        </thead>
                        <tbody>${buyoutRows}</tbody>
                    </table>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Время доставки</div>
                <div class="metric-caption">Как доставочные SLA влияют на финансы</div>
                <div class="metric-table-wrapper">
                    <table class="metric-table">
                        <thead>
                            <tr><th>Часы</th><th class="num">Прибыль/шт</th><th class="num">%</th></tr>
                        </thead>
                        <tbody>${delivRows}</tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    elements.sensitivity.classList.remove('hidden');
}

// Создание строки таблицы
function createRow(label, fboValue, fbsValue, fboPercent, fbsPercent, type, expandable = false, highlighted = false) {
    const rowClass = highlighted ? 'table-row highlighted' : 'table-row';
    const expandIcon = expandable ? '<span class="expand-icon">▸</span>' : '';
    
    return `
        <div class="${rowClass}">
            <div class="row-label">
                ${expandIcon}${label}
            </div>
            <div class="row-value">
                <div class="value-amount ${type}">${formatNumber(fboValue)} ₽</div>
                <div class="value-percent">${formatPercent(fboPercent)}%</div>
                ${createProgressBar(fboPercent, type)}
            </div>
            <div class="row-value">
                <div class="value-amount ${type}">${formatNumber(fbsValue)} ₽</div>
                <div class="value-percent">${formatPercent(fbsPercent)}%</div>
                ${createProgressBar(fbsPercent, type)}
            </div>
        </div>
    `;
}

// Создание строки итога
function createTotalRow(label, fboValue, fbsValue) {
    return `
        <div class="table-row total">
            <div class="row-label">${label}</div>
            <div class="row-value">
                <div class="value-amount positive">${formatNumber(fboValue)} ₽</div>
            </div>
            <div class="row-value">
                <div class="value-amount positive">${formatNumber(fbsValue)} ₽</div>
            </div>
        </div>
    `;
}

// Создание progress bar
function createProgressBar(percent, type) {
    const absPercent = Math.abs(parseFloat(percent));
    const width = Math.min(absPercent, 100);
    return `
        <div class="progress-bar">
            <div class="progress-fill ${type}" style="width: ${width}%"></div>
        </div>
    `;
}

// Строка с оффсет-баром
function createOffsetRow(label, fboValue, fbsValue, fboPercent, fbsPercent, fboOffset, fbsOffset, colorClass, expandable = false, highlighted = false) {
    const rowClass = highlighted ? 'table-row highlighted' : 'table-row';
    const expandIcon = expandable ? '<span class="expand-icon">▸</span>' : '';
    const pFbo = Math.abs(parseFloat(fboPercent));
    const pFbs = Math.abs(parseFloat(fbsPercent));
    const oFbo = Math.max(0, Math.min(100, parseFloat(fboOffset) || 0));
    const oFbs = Math.max(0, Math.min(100, parseFloat(fbsOffset) || 0));
    const wFbo = Math.min(100 - oFbo, pFbo);
    const wFbs = Math.min(100 - oFbs, pFbs);
    
    return `
        <div class="${rowClass}">
            <div class="row-label">${expandIcon}${label}</div>
            <div class="row-value">
                <div class="value-amount negative">${formatNumber(fboValue)} ₽</div>
                <div class="value-percent">${formatPercent(pFbo)}%</div>
                <div class="progress-stacked">
                    <div class="progress-seg ${colorClass}" style="left:${oFbo}%; width:${wFbo}%"></div>
                </div>
            </div>
            <div class="row-value">
                <div class="value-amount negative">${formatNumber(fbsValue)} ₽</div>
                <div class="value-percent">${formatPercent(pFbs)}%</div>
                <div class="progress-stacked">
                    <div class="progress-seg ${colorClass}" style="left:${oFbs}%; width:${wFbs}%"></div>
                </div>
            </div>
        </div>
    `;
}

// Строка с многоцветным прогресс-баром (Цена товара)
function createPriceRow(label, fbo, fbs, parts) {
    const row = `
        <div class="table-row">
            <div class="row-label">${label}</div>
            <div class="row-value">
                <div class="value-amount positive">${formatNumber(fbo.price)} ₽</div>
                <div class="value-percent">100%</div>
                ${createTripleBar(parts.fboBlue, parts.fboGray, parts.fboGreen)}
            </div>
            <div class="row-value">
                <div class="value-amount positive">${formatNumber(fbs.price)} ₽</div>
                <div class="value-percent">100%</div>
                ${createTripleBar(parts.fbsBlue, parts.fbsGray, parts.fbsGreen)}
            </div>
        </div>
    `;
    return row;
}

function createTripleBar(blue, gray, green) {
    const clamp = (v) => Math.max(0, Math.min(100, v));
    const b = clamp(blue);
    const g1 = clamp(gray);
    let g2 = clamp(green);
    // Нормализация чтобы сумма не превышала 100
    const sum = b + g1 + g2;
    if (sum > 100) {
        const k = 100 / sum;
        g2 = (g2 * k);
    }
    return `
        <div class="progress-multi">
            <div class="seg-blue" style="width:${b}%"></div>
            <div class="seg-gray" style="width:${g1}%"></div>
            <div class="seg-green" style="width:${g2}%"></div>
        </div>
    `;
}

// Форматирование числа
function formatNumber(value) {
    const num = Number(parseFloat(value));
    if (!isFinite(num)) return '0';
    return num.toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function formatPercent(value) {
    const num = Number(parseFloat(value));
    if (!isFinite(num)) return '0.00';
    return num.toFixed(2);
}

// Показать ошибку
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.remove('hidden');
    elements.resultsTable.classList.add('hidden');
}

// Сброс формы
function resetForm() {
    elements.categorySearch.value = '';
    selectedCategory = null;
    elements.categoryCommissions.classList.add('hidden');
    elements.price.value = '805';
    elements.weight.value = '0.15';
    elements.length.value = '27';
    elements.width.value = '24';
    elements.height.value = '2';
    elements.volumeInput.value = '1.296';
    elements.buyoutRate.value = '90';
    elements.deliveryTime.value = '45';
    elements.costPrice.value = '215';
    elements.otherCosts.value = '10';
    elements.monthlySales.value = '1000';
    elements.adCosts.value = '10';
    
    // Сброс налога на 6%
    elements.taxRate.value = '6';
    
    // Режим габаритов
    switchMode('dimensions');
    
    // Очистка результатов
    elements.resultsTable.innerHTML = '';
    elements.errorMessage.classList.add('hidden');
    
    updateCalculatedVolume();
    elements.kpiTiles.classList.add('hidden');
    elements.breakdowns.classList.add('hidden');
    elements.sensitivity.classList.add('hidden');
}


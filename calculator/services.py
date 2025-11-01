from decimal import Decimal
from typing import Dict, Any
from categories.models import Category


class OzonCalculator:
    """
    Сервис для расчета юнит-экономики товаров на Ozon
    """
    
    # Константы для расчетов (в процентах и рублях)
    ACQUIRING_RATE = Decimal('2.0')  # Эквайринг 2%
    
    # Таблица логистики Ozon для товаров до 300₽ (объем в литрах -> стоимость в рублях)
    LOGISTICS_TABLE_UNDER_300 = [
        (Decimal('0.2'), Decimal('40')),
        (Decimal('0.3'), Decimal('44')),
        (Decimal('0.5'), Decimal('48')),
        (Decimal('1'), Decimal('56')),
        (Decimal('2'), Decimal('66')),
        (Decimal('3'), Decimal('76')),
        (Decimal('5'), Decimal('96')),
        (Decimal('10'), Decimal('146')),
        (Decimal('20'), Decimal('216')),
        (Decimal('30'), Decimal('306')),
        (Decimal('50'), Decimal('426')),
        (Decimal('100'), Decimal('786')),
        (Decimal('190'), Decimal('792')),
    ]
    
    # Таблица коэффициентов и процентов от цены в зависимости от времени доставки (часы)
    # Формат: (часы, коэффициент к базовому тарифу, процент от цены товара)
    DELIVERY_TIME_COEFFICIENTS = [
        (29, Decimal('1.000'), Decimal('0.00')),
        (30, Decimal('1.050'), Decimal('0.25')),
        (31, Decimal('1.110'), Decimal('0.55')),
        (32, Decimal('1.160'), Decimal('0.80')),
        (33, Decimal('1.230'), Decimal('1.15')),
        (34, Decimal('1.280'), Decimal('1.40')),
        (35, Decimal('1.320'), Decimal('1.60')),
        (36, Decimal('1.360'), Decimal('1.80')),
        (37, Decimal('1.400'), Decimal('2.00')),
        (38, Decimal('1.440'), Decimal('2.20')),
        (39, Decimal('1.480'), Decimal('2.40')),
        (40, Decimal('1.510'), Decimal('2.55')),
        (41, Decimal('1.540'), Decimal('2.70')),
        (42, Decimal('1.570'), Decimal('2.85')),
        (43, Decimal('1.600'), Decimal('3.00')),
        (44, Decimal('1.630'), Decimal('3.15')),
        (45, Decimal('1.660'), Decimal('3.30')),
        (46, Decimal('1.690'), Decimal('3.45')),
        (47, Decimal('1.710'), Decimal('3.55')),
        (48, Decimal('1.730'), Decimal('3.65')),
        (49, Decimal('1.750'), Decimal('3.75')),
        (50, Decimal('1.760'), Decimal('3.80')),
        (51, Decimal('1.770'), Decimal('3.85')),
        (52, Decimal('1.774'), Decimal('3.87')),
        (53, Decimal('1.780'), Decimal('3.90')),
        (54, Decimal('1.784'), Decimal('3.92')),
        (55, Decimal('1.788'), Decimal('3.94')),
        (56, Decimal('1.790'), Decimal('3.95')),
        (57, Decimal('1.792'), Decimal('3.96')),
        (58, Decimal('1.794'), Decimal('3.97')),
        (59, Decimal('1.796'), Decimal('3.98')),
        (60, Decimal('1.798'), Decimal('3.99')),
        (61, Decimal('1.800'), Decimal('4.00')),
    ]
    
    def __init__(self, category_id: int, price: Decimal, weight: Decimal, volume: Decimal,
                 tax_rate: Decimal, buyout_rate: Decimal, delivery_time: int,
                 ad_costs_rate: Decimal, cost_price: Decimal, other_costs: Decimal,
                 monthly_sales: int):
        """
        Инициализация калькулятора
        """
        self.category = Category.objects.get(id=category_id)
        self.price = price
        self.weight = weight
        self.volume = volume
        self.tax_rate = tax_rate / Decimal('100')  # Конвертируем % в десятичную дробь
        self.buyout_rate = buyout_rate / Decimal('100')
        self.delivery_time = delivery_time
        self.ad_costs_rate = ad_costs_rate / Decimal('100')
        self.cost_price = cost_price
        self.other_costs = other_costs
        self.monthly_sales = monthly_sales
    
    def calculate_ozon_reward(self, commission_rate: Decimal) -> Decimal:
        """
        Расчет вознаграждения Ozon (комиссия)
        """
        return (self.price * commission_rate) / Decimal('100')
    
    def get_delivery_time_adjustments(self) -> tuple[Decimal, Decimal]:
        """
        Получить коэффициент и процент от цены для времени доставки
        
        Returns:
            tuple: (коэффициент, процент от цены)
        """
        # Если время доставки меньше 29 часов - используем минимальные значения
        if self.delivery_time <= 29:
            return (Decimal('1.000'), Decimal('0.00'))
        
        # Если время доставки больше 61 часа - используем максимальные значения
        if self.delivery_time >= 61:
            return (Decimal('1.800'), Decimal('4.00'))
        
        # Ищем точное совпадение или ближайшее меньшее значение
        for hours, coeff, percent in self.DELIVERY_TIME_COEFFICIENTS:
            if self.delivery_time <= hours:
                return (coeff, percent)
        
        # На случай, если не нашли - возвращаем максимальные значения
        return (Decimal('1.800'), Decimal('4.00'))
    
    def calculate_acquiring(self) -> Decimal:
        """
        Расчет эквайринга (оплата банковских услуг)
        """
        return (self.price * self.ACQUIRING_RATE) / Decimal('100')
    
    def calculate_base_logistics(self, price_override: Decimal = None) -> Decimal:
        """
        Расчет базового тарифа логистики (без учёта времени доставки)
        Зависит только от цены товара и объема (в литрах)
        
        Формула Ozon:
        - Для товаров ≤300₽: таблица по объему или 792₽ (если >190л)
        - Для товаров >300₽: ступенчатая шкала по объему
        
        Args:
            price_override: Опциональная цена для пересчета (используется при расчете точек цены)
        """
        volume_liters = self.volume  # Объем уже в литрах
        price_for_calc = price_override if price_override is not None else self.price
        
        # Ограничиваем объем для расчета (максимум 2112 литров)
        volume_for_calc = min(volume_liters, Decimal('2112'))
        
        if price_for_calc <= Decimal('300'):
            # Блок 1: товары до 300₽
            if volume_for_calc > Decimal('190'):
                return Decimal('792')  # Максимальная ставка для дешевых товаров
            
            # Поиск в таблице логистики
            for max_volume, cost in self.LOGISTICS_TABLE_UNDER_300:
                if volume_liters <= max_volume:
                    return cost
            
            # Если объем больше всех значений в таблице
            return Decimal('792')
        else:
            # Блок 2: товары свыше 300₽
            volume_rounded = int(volume_liters.to_integral_value(rounding='ROUND_UP'))
            
            if volume_rounded <= 1:
                return Decimal('46')
            elif volume_rounded <= 2:
                return Decimal('56')
            elif volume_rounded <= 3:
                return Decimal('66')
            elif volume_rounded <= 190:
                # 66 + (литры - 3) × 15
                return Decimal('66') + (Decimal(str(volume_rounded)) - Decimal('3')) * Decimal('15')
            else:
                return Decimal('2871')  # Максимальная ставка для дорогих товаров
    
    def calculate_processing_and_delivery(self, price_override: Decimal = None) -> Decimal:
        """
        Расчет стоимости обработки и доставки (логистики FBO Ozon)
        Зависит от цены товара, объема (в литрах) и времени доставки
        
        Формула Ozon:
        - Шаг 1: Расчет базового тарифа по объему
        - Шаг 2: Применение коэффициента и процента от цены по времени доставки
          - Итого = (Базовый_тариф × Коэффициент) + (Цена × Процент / 100)
        
        Args:
            price_override: Опциональная цена для пересчета (используется при расчете точек цены)
        """
        price_for_calc = price_override if price_override is not None else self.price
        
        # Шаг 1: Получаем базовый тариф логистики
        base_logistics = self.calculate_base_logistics(price_override=price_for_calc)
        
        # Шаг 2: Применение коэффициента и процента от цены по времени доставки
        coeff, price_percent = self.get_delivery_time_adjustments()
        
        # Итоговая логистика = (Базовый тариф × Коэффициент) + (Цена × Процент / 100)
        final_logistics = (base_logistics * coeff) + (price_for_calc * price_percent / Decimal('100'))
        
        return final_logistics
    
    def calculate_returns_and_cancellations(self, price_override: Decimal = None) -> Decimal:
        """
        Расчет затрат на возвраты и отмены (обратная логистика)
        
        Тариф на обратную логистику равен тарифу на логистику,
        но не учитывает среднее время доставки до покупателя.
        
        Также учитывается процент выкупа: оплачивается доля невыкупленных/отмененных
        отправлений. То есть используется базовый тариф, умноженный на (1 - выкуп).
        
        Args:
            price_override: Опциональная цена для пересчета (используется при расчете точек цены)
        """
        base = self.calculate_base_logistics(price_override=price_override)
        not_buyout_share = Decimal('1') - self.buyout_rate  # доля невыкупа
        if not_buyout_share < 0:
            not_buyout_share = Decimal('0')
        return base * not_buyout_share
    
    def calculate_profit_tax(self) -> Decimal:
        """
        Расчет налога - считается от цены товара
        """
        return self.price * self.tax_rate
    
    def calculate_for_scheme(self, commission_rate: Decimal, scheme_name: str) -> Dict[str, Any]:
        """
        Расчет для конкретной схемы работы (FBO или FBS)
        """
        # Вспомогательная функция для пересчета по произвольной цене (для sensitivity/поиска цены)
        def compute_net_profit_for_price(test_price: Decimal) -> Dict[str, Decimal]:
            # Комиссия Ozon
            ozon_reward_local = (test_price * commission_rate) / Decimal('100')
            # Эквайринг
            acquiring_local = (test_price * self.ACQUIRING_RATE) / Decimal('100')
            # Логистика разбивка - пересчитываем полностью от новой цены
            base_logistics_local = self.calculate_base_logistics(price_override=test_price)
            coeff_local, price_pct_local = self.get_delivery_time_adjustments()
            price_component_local = (test_price * price_pct_local) / Decimal('100')
            processing_delivery_local = (base_logistics_local * coeff_local) + price_component_local
            # Возвраты - пересчитываем полностью от новой цены
            returns_local = self.calculate_returns_and_cancellations(price_override=test_price)
            # Сумма озон-расходов
            total_ozon_costs_local = ozon_reward_local + acquiring_local + processing_delivery_local + returns_local
            profit_before_costs_local = test_price - total_ozon_costs_local
            profit_tax_local = test_price * self.tax_rate
            net_profit_local = profit_before_costs_local - self.cost_price - profit_tax_local - self.other_costs
            return {
                'net_profit': net_profit_local,
                'total_ozon_costs': total_ozon_costs_local,
                'profit_before_costs': profit_before_costs_local,
                'base_logistics': base_logistics_local,
                'coeff': coeff_local,
                'price_component': price_component_local,
                'returns': returns_local
            }

        # 1. Вознаграждение Ozon (комиссия)
        ozon_reward = self.calculate_ozon_reward(commission_rate)
        
        # 2. Эквайринг
        acquiring = self.calculate_acquiring()
        
        # 3. Обработка и доставка
        processing_delivery = self.calculate_processing_and_delivery()
        base_logistics_now = self.calculate_base_logistics()
        coeff_now, price_percent_now = self.get_delivery_time_adjustments()
        price_component_now = (self.price * price_percent_now) / Decimal('100')
        
        # 4. Возвраты и отмены
        returns_cancellations = self.calculate_returns_and_cancellations()
        
        # 5. Общие затраты на Ozon за штуку
        total_ozon_costs = ozon_reward + acquiring + processing_delivery + returns_cancellations
        
        # 6. К начислению за товар (прибыль до вычета собственных затрат)
        profit_before_costs = self.price - total_ozon_costs
        
        # 7. Налог (считается от цены товара)
        profit_tax = self.calculate_profit_tax()
        
        # 8. Вычитаем себестоимость, налог и прочие затраты
        net_profit_per_unit = profit_before_costs - self.cost_price - profit_tax - self.other_costs
        
        # 10. Прибыль за партию (месячную продажу)
        net_profit_total = net_profit_per_unit * Decimal(str(self.monthly_sales))
        annual_net_profit = net_profit_total * Decimal('12')
        
        # Contribution metrics
        gross_margin_before_tax = (profit_before_costs - self.cost_price - self.other_costs)
        
        # Расчет процентов для визуализации
        def calc_percent(value: Decimal) -> Decimal:
            if self.price == 0:
                return Decimal('0')
            return (value / self.price) * Decimal('100')
        
        # Break-even price (поиск цены, при которой net_profit_per_unit = 0)
        def find_price_for_target_net(target_net: Decimal) -> Decimal:
            low = Decimal('0.01')
            high = max(self.price * Decimal('2'), Decimal('1000'))
            for _ in range(40):
                mid = (low + high) / 2
                res = compute_net_profit_for_price(mid)
                if res['net_profit'] > target_net:
                    high = mid
                else:
                    low = mid
            return (low + high) / 2
        
        break_even_price = find_price_for_target_net(Decimal('0'))
        
        # Target price для маржи 10% и 20% (по net_profit_per_unit_percent)
        def find_price_for_margin(target_margin_pct: Decimal) -> Decimal:
            low = Decimal('0.01')
            high = max(self.price * Decimal('2'), Decimal('1000'))
            for _ in range(40):
                mid = (low + high) / 2
                res = compute_net_profit_for_price(mid)
                # Маржа должна рассчитываться от тестовой цены (mid), а не от текущей (self.price)
                if mid == 0:
                    margin = Decimal('0')
                else:
                    margin = (res['net_profit'] / mid) * Decimal('100')
                if margin >= target_margin_pct:
                    high = mid
                else:
                    low = mid
            return (low + high) / 2
        
        target_price_10pct = find_price_for_margin(Decimal('10'))
        target_price_20pct = find_price_for_margin(Decimal('20'))
        
        # Sensitivity arrays
        def to_row_price(delta_pct: int):
            test_price = self.price * (Decimal('1') + Decimal(delta_pct) / Decimal('100'))
            res = compute_net_profit_for_price(test_price)
            # Процент маржи должен рассчитываться от тестовой цены, а не от текущей
            if test_price == 0:
                margin_percent = Decimal('0')
            else:
                margin_percent = (res['net_profit'] / test_price) * Decimal('100')
            return {
                'delta_pct': delta_pct,
                'price': round(test_price, 2),
                'net_profit_per_unit': round(res['net_profit'], 2),
                'net_profit_per_unit_percent': round(margin_percent, 2)
            }
        
        price_sensitivity = [to_row_price(d) for d in (-10, -5, 0, 5, 10)]
        
        def to_row_buyout(rate: int):
            old = self.buyout_rate
            self.buyout_rate = Decimal(rate) / Decimal('100')
            res = compute_net_profit_for_price(self.price)
            self.buyout_rate = old
            return {
                'buyout_rate': rate,
                'net_profit_per_unit': round(res['net_profit'], 2),
                'net_profit_per_unit_percent': round(calc_percent(res['net_profit']), 2)
            }
        buyout_sensitivity = [to_row_buyout(r) for r in (80, 85, 90, 95)]
        
        def to_row_delivery(hours: int):
            old = self.delivery_time
            self.delivery_time = hours
            res = compute_net_profit_for_price(self.price)
            self.delivery_time = old
            return {
                'hours': hours,
                'net_profit_per_unit': round(res['net_profit'], 2),
                'net_profit_per_unit_percent': round(calc_percent(res['net_profit']), 2)
            }
        delivery_sensitivity = [to_row_delivery(h) for h in (29, 35, 45, 55, 61)]
        
        return {
            'scheme': scheme_name,
            'price': round(self.price, 2),
            'price_percent': Decimal('100.00'),
            
            'ozon_reward': -round(ozon_reward, 2),
            'ozon_reward_percent': round(calc_percent(ozon_reward), 2),
            
            'acquiring': -round(acquiring, 2),
            'acquiring_percent': round(calc_percent(acquiring), 2),
            
            'processing_delivery': -round(processing_delivery, 2),
            'processing_delivery_percent': round(calc_percent(processing_delivery), 2),
            
            'returns_cancellations': -round(returns_cancellations, 2),
            'returns_cancellations_percent': round(calc_percent(returns_cancellations), 2),
            
            'total_ozon_costs': -round(total_ozon_costs, 2),
            'total_ozon_costs_percent': round(calc_percent(total_ozon_costs), 2),
            
            'profit_before_costs': round(profit_before_costs, 2),
            'profit_before_costs_percent': round(calc_percent(profit_before_costs), 2),
            
            'cost_price': -round(self.cost_price, 2),
            'cost_price_percent': round(calc_percent(self.cost_price), 2),
            
            'profit_tax': -round(profit_tax, 2),
            'profit_tax_percent': round(calc_percent(profit_tax), 2),
            
            'other_costs': -round(self.other_costs, 2),
            'other_costs_percent': round(calc_percent(self.other_costs), 2),
            
            'net_profit_per_unit': round(net_profit_per_unit, 2),
            'net_profit_per_unit_percent': round(calc_percent(net_profit_per_unit), 2),
            
            'net_profit_total': round(net_profit_total, 2),
            'annual_net_profit': round(annual_net_profit, 2),
            'gross_margin_before_tax': round(gross_margin_before_tax, 2),
            'gross_margin_before_tax_percent': round(calc_percent(gross_margin_before_tax), 2),
            'effective_ozon_fee_percent': round(calc_percent(total_ozon_costs), 2),
            'break_even_price': round(break_even_price, 2),
            'target_price_10pct': round(target_price_10pct, 2),
            'target_price_20pct': round(target_price_20pct, 2),
            'logistics_breakdown': {
                'base': round(base_logistics_now, 2),
                'time_coeff': round(coeff_now, 3),
                'price_percent_component': round(price_component_now, 2)
            },
            'returns_breakdown': {
                'base': round(base_logistics_now, 2),
                'not_buyout_share': round(Decimal('1') - self.buyout_rate, 3)
            },
            'sensitivity': {
                'price': price_sensitivity,
                'buyout': buyout_sensitivity,
                'delivery_time': delivery_sensitivity
            }
        }
    
    def calculate_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Расчет для обеих схем работы (FBO и FBS)
        """
        fbo_results = self.calculate_for_scheme(self.category.fbo_commission, 'FBO')
        fbs_results = self.calculate_for_scheme(self.category.fbs_commission, 'FBS')
        
        return {
            'fbo_results': fbo_results,
            'fbs_results': fbs_results,
        }








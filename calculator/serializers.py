from rest_framework import serializers
from decimal import Decimal


class LogisticsBreakdownSerializer(serializers.Serializer):
    base = serializers.DecimalField(max_digits=12, decimal_places=2)
    time_coeff = serializers.DecimalField(max_digits=6, decimal_places=3)
    price_percent_component = serializers.DecimalField(max_digits=12, decimal_places=2)


class ReturnsBreakdownSerializer(serializers.Serializer):
    base = serializers.DecimalField(max_digits=12, decimal_places=2)
    not_buyout_share = serializers.DecimalField(max_digits=5, decimal_places=3)


class SensitivityPriceRowSerializer(serializers.Serializer):
    delta_pct = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit_per_unit_percent = serializers.DecimalField(max_digits=7, decimal_places=2)


class SensitivityBuyoutRowSerializer(serializers.Serializer):
    buyout_rate = serializers.IntegerField()
    net_profit_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit_per_unit_percent = serializers.DecimalField(max_digits=7, decimal_places=2)


class SensitivityDeliveryRowSerializer(serializers.Serializer):
    hours = serializers.IntegerField()
    net_profit_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit_per_unit_percent = serializers.DecimalField(max_digits=7, decimal_places=2)


class SensitivitySerializer(serializers.Serializer):
    price = SensitivityPriceRowSerializer(many=True)
    buyout = SensitivityBuyoutRowSerializer(many=True)
    delivery_time = SensitivityDeliveryRowSerializer(many=True)


class CalculationInputSerializer(serializers.Serializer):
    """
    Serializer для входных данных расчета юнит-экономики
    """
    # ID категории
    category_id = serializers.IntegerField(required=True, help_text='ID категории товара')
    
    # Основные параметры товара
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0.01'),
        help_text='Цена товара в рублях'
    )
    weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=True,
        min_value=Decimal('0.001'),
        help_text='Вес товара в кг'
    )
    
    # Режим ввода размеров
    dimension_mode = serializers.ChoiceField(
        choices=['dimensions', 'volume'],
        required=True,
        help_text='Режим ввода: dimensions (габариты) или volume (объем)'
    )
    
    # Габариты (опционально, для режима dimensions)
    length = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0.01'),
        help_text='Длина в см (требуется для режима dimensions)'
    )
    width = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0.01'),
        help_text='Ширина в см (требуется для режима dimensions)'
    )
    height = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0.01'),
        help_text='Высота в см (требуется для режима dimensions)'
    )
    
    # Объем (опционально, для режима volume)
    volume = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        min_value=Decimal('0.001'),
        help_text='Объем в литрах (требуется для режима volume)'
    )
    
    # Параметры для расчета прибыли
    tax_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        help_text='Налог на прибыль в процентах'
    )
    buyout_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        help_text='Процент выкупа'
    )
    delivery_time = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text='Время доставки в часах'
    )
    ad_costs_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        help_text='Доля рекламных расходов в процентах'
    )
    
    # Затраты
    cost_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0'),
        help_text='Себестоимость за 1 шт в рублях'
    )
    other_costs = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0'),
        help_text='Прочие затраты на 1 шт в рублях'
    )
    monthly_sales = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text='Количество продаж в месяц в штуках'
    )
    
    def validate(self, data):
        """
        Дополнительная валидация в зависимости от режима ввода
        """
        dimension_mode = data.get('dimension_mode')
        
        if dimension_mode == 'dimensions':
            # Проверяем наличие всех габаритов
            if not all([data.get('length'), data.get('width'), data.get('height')]):
                raise serializers.ValidationError(
                    'Для режима "dimensions" необходимо указать длину, ширину и высоту'
                )
            # Вычисляем объем из габаритов (L × W × H / 1000)
            length = data['length']
            width = data['width']
            height = data['height']
            data['volume'] = (length * width * height) / Decimal('1000')
            
        elif dimension_mode == 'volume':
            # Проверяем наличие объема
            if not data.get('volume'):
                raise serializers.ValidationError(
                    'Для режима "volume" необходимо указать объем'
                )
        
        return data


class CalculationResultSerializer(serializers.Serializer):
    """
    Serializer для результатов расчета
    """
    scheme = serializers.CharField(help_text='Схема работы: FBO или FBS')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Цена товара')
    price_percent = serializers.DecimalField(max_digits=5, decimal_places=2, help_text='Процент от цены')
    
    ozon_reward = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Вознаграждение Ozon')
    ozon_reward_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    acquiring = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Эквайринг')
    acquiring_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    processing_delivery = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Обработка и доставка')
    processing_delivery_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    returns_cancellations = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Возвраты и отмены')
    returns_cancellations_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    total_ozon_costs = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Общие затраты на Ozon')
    total_ozon_costs_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    profit_before_costs = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='К начислению за товар')
    profit_before_costs_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Себестоимость товара')
    cost_price_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    profit_tax = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Налог на прибыль')
    profit_tax_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    other_costs = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Прочие затраты')
    other_costs_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    net_profit_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Прибыль за штуку')
    net_profit_per_unit_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    net_profit_total = serializers.DecimalField(max_digits=14, decimal_places=2, help_text='Прибыль за партию')
    annual_net_profit = serializers.DecimalField(max_digits=14, decimal_places=2, help_text='Прибыль за год')
    gross_margin_before_tax = serializers.DecimalField(max_digits=12, decimal_places=2, help_text='Валовая до налога')
    gross_margin_before_tax_percent = serializers.DecimalField(max_digits=7, decimal_places=2)
    effective_ozon_fee_percent = serializers.DecimalField(max_digits=7, decimal_places=2)
    break_even_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_price_10pct = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_price_20pct = serializers.DecimalField(max_digits=10, decimal_places=2)
    logistics_breakdown = LogisticsBreakdownSerializer()
    returns_breakdown = ReturnsBreakdownSerializer()
    sensitivity = SensitivitySerializer()


class CalculationOutputSerializer(serializers.Serializer):
    """
    Serializer для выходных данных расчета
    """
    fbo_results = CalculationResultSerializer(help_text='Результаты для схемы FBO')
    fbs_results = CalculationResultSerializer(help_text='Результаты для схемы FBS')









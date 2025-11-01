from django.db import models


class Category(models.Model):
    """
    Модель категории товара на Ozon с комиссиями для схем FBO и FBS
    """
    name = models.CharField(
        max_length=255,
        verbose_name='Тип товара',
        db_index=True,
        help_text='Тип/название товара (например: "Шарф", "3D-очки")'
    )
    category_group = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Категория',
        db_index=True,
        help_text='Группа/категория товара (например: "Аксессуары", "VR-устройства и аксессуары")'
    )
    fbo_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Комиссия FBO (%)',
        help_text='Комиссия для схемы работы FBO (Fulfillment by Ozon) в процентах'
    )
    fbs_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Комиссия FBS (%)',
        help_text='Комиссия для схемы работы FBS (Fulfillment by Seller) в процентах'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'
        ordering = ['name']
        unique_together = [['name', 'category_group']]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category_group']),
        ]

    def __str__(self):
        if self.category_group:
            return f"{self.name} ({self.category_group}) - FBO: {self.fbo_commission}%, FBS: {self.fbs_commission}%"
        return f"{self.name} (FBO: {self.fbo_commission}%, FBS: {self.fbs_commission}%)"

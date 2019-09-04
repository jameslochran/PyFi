import django_tables2 as tables

class PortfolioTable(tables.Table):
    class Meta:
        model = Portfolio

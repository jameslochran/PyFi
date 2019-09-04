from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Portfolio, Stock
from .forms import SearchForm, StockForm
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import urllib
import requests
import pandas as pd
from django_pandas.io import read_frame
import datetime
from datetime import datetime, timedelta
import yfinance as yf
import pandas_highcharts
from pandas_highcharts.core import serialize
from iexfinance.stocks import get_historical_data
import dateutil.parser
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import numpy as np




#global variables
dataset = pd.read_csv("export_symbols.csv",  usecols=["symbol", "name"]).copy()
dataset.set_index('name', inplace=True)

sp_500_histdata = pd.read_csv("sp500_export.csv", parse_dates= ["Date"], index_col = "Date")



# from django.forms import formset_factory

# Create your views here.
def home(request):
    ports = Portfolio.objects.all().order_by('id')[:3]

    return render(request,'home.html', {'ports': ports})

@login_required
def dashboard(request):
    ports = Portfolio.objects.filter(user=request.user)

    return render(request,'dashboard.html', {'ports':ports})



def dash_Total(request, pk):
    df1 = get_Port_Total(pk)
    portfolio_value = df1['total'].sum()
    print(portfolio_value)
    return render(request,'dashboard.html', {'portfolio_value':portfolio_value})


# @login_required
# def add_Stock(request, pk):
#     # VideoFormSet = formset_factory(VideoForm, extra=5)
#     form = StockForm()
#     # form = VideoFormSet()
#     # search_form = SearchForm()
#     port = Portfolio.objects.get(pk=pk)
#     if not port.user == request.user:
#         raise Http404
#
#     # if form:
#     if request.method == 'POST':
#         #create
#         form = StockForm(request.POST)
#         if form.is_valid():
#             stock = Stock()
#             stock.portfolio = port
#             stock.ticker = form.cleaned_data['ticker']
#             stock.count = form.cleaned_data['count']
#             stock.unit_cost = form.cleaned_data['unit_cost']
#             stock.acq_date = form.cleaned_data['acq_date']
#
#             # if stock_id:
#             stock.save()
#
#             return redirect('detail_portfolio', pk)
#
#
#     return render(request, 'add_stock.html', {'form':form,  'port':port})
@login_required
def add_Stock(request, pk):
    portfolio = Portfolio.objects.get(pk=pk)
    StockFormset = inlineformset_factory(Portfolio, Stock, fields = ('ticker', 'count', 'unit_cost', 'acq_date'))

    if request.method == 'POST':
        formset = StockFormset(request.POST,instance=portfolio)
        if formset.is_valid():
            formset.save()

            return redirect('detail_portfolio', pk=pk)

    formset = StockFormset(instance=portfolio)


    return render(request, 'add_stock.html', {'formset': formset,'portfolio':portfolio})




@login_required
def stock_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():

        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form!'})

@login_required
def lookup(request):
    import json
    if request.method == 'POST':
        ticker = request.POST['ticker']
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ ticker +"/quote?token=pk_5a6bfc8f3d3d405f910aec024cc2bc14")

        try:
            api = json.loads(api_request.content)


        except Exception as e:
            api = "Error...."

        return render(request, 'lookup.html', {'api' : api, "ticker":ticker, "api_request":api_request})

    return render(request, 'lookup.html')

@login_required
def research(request):
    if request.method == "POST":
        companyName = request.POST['companyName']
        # dataset = pd.read_csv("export_symbols.csv",  usecols=["symbol", "name"]).copy()
        # dataset.set_index('name', inplace=True)

        try:
            ticker = dataset.filter(like=companyName, axis=0)
            ticker = ticker.to_html(classes='table table-striped table-hover', index_names=False)

        except Exception as e:
            symbol = "Error...."
        return render(request, 'research.html',{"ticker":ticker, "companyName":companyName})
    return render(request, "research.html")



@login_required
def symbol(request):
    from iexfinance.refdata import get_symbols
    symbols = get_symbols(output_format='pandas', token="pk_5a6bfc8f3d3d405f910aec024cc2bc14")
    export = symbols.to_csv(r'C:\Users\James\Desktop\export_symbols.csv', index=None, header=True)


    return render(request, 'symbol.html', {"symbols":symbols})


class DeleteStock(LoginRequiredMixin, generic.DeleteView):
    model = Stock
    template_name = 'delete_stock.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        stock = super(DeleteStock, self).get_object()
        if not stock.portfolio.user == self.request.user:
            raise Http404
        return stock

class UpdateStock(LoginRequiredMixin, generic.UpdateView):
    model = Stock
    template_name = 'update_stock.html'
    fields = ['ticker', 'count', 'acq_date', 'unit_cost']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        stock = super(UpdateStock, self).get_object()
        if not stock.portfolio.user == self.request.user:
            raise Http404
        return stock



class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


#crud
class CreatePortfolio(LoginRequiredMixin, generic.CreateView):
    model = Portfolio
    fields = ['title', 'description', 'type']
    template_name = 'create_portfolio.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreatePortfolio, self).form_valid(form)
        return redirect('dashboard')

class DetailPortfolio(generic.DetailView):
    model = Portfolio

    qs = Portfolio.objects.all()
    df = read_frame(qs)
    template_name = 'detail_portfolio.html'



def getPrice(ticker):
    import json
    api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ ticker +"/quote?token=pk_5a6bfc8f3d3d405f910aec024cc2bc14")
    try:
        api = json.loads(api_request.content)
        api = api["latestPrice"]
    except Exception as e:
        api = "Error...."

    return api

def sp500():

    data = yf.download("^GSPC", start="2013-12-31", end="2019-08-01")
    data.drop(columns=['Open', 'High', 'Low', 'Volume', 'Close'], inplace=True)
    sp_500_export = data.to_csv(r'C:\Users\James\Desktop\sp500_export.csv', header=True)

    return data

def sp500_Current(d):
    US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    result = d - 1 * US_BUSINESS_DAY
    pday = result.to_pydatetime().date()
    try:
        data = yf.download("^GSPC", start=pday, end=pday)
        data.drop(columns=['Open', 'High', 'Low', 'Volume', 'Close'], inplace=True)
    except Exception as e:
        data = "Error - there was an issue with getting the closing price for the SP500."
    return data['Adj Close']


def getSP500Unit(d):
    US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    result = d - 1 * US_BUSINESS_DAY
    pday = result.to_pydatetime().date()
    print(pday)

    try:
        data = yf.download("^GSPC", start=pday, end=pday)
        data.drop(columns=['Open', 'High', 'Low', 'Volume', 'Close'], inplace=True)
    except Exception as e:
        data = "Error - there was an issue with getting the closing price for the SP500."
    return data['Adj Close'][0]

    # try:
    #     sp_cost = sp_500_histdata.loc[d]
    # except Exception as e:
    #     sp_cost = "Error - Please ensure you have entered a valid trading date for your stock purchase date"
    # return sp_cost['Adj Close']

def ann_risk_return(returns_df):
    summary = returns_df.agg(["mean", "std"]).T
    summary.columns = ["Return", "Risk"]
    summary.Return = summary.Return*252
    summary.Risk = summary.Risk * np.sqrt(252)
    return summary

def color_negative_red(value):
  """
  Colors elements in a dateframe
  green if positive and red if
  negative. Does not color NaN
  values.
  """

  if value < 0:
    color = 'red'
  elif value > 0:
    color = 'green'
  else:
    color = 'black'

  return 'color: %s' % color

def get_Port_Total(pk):
    qs = Stock.objects.filter(portfolio_id = pk)
    df = read_frame(qs, fieldnames=['ticker', 'count', 'unit_cost', 'acq_date'])
    # df1 = qs1.to_dataframe(['ticker', 'count'], index='ticker')
    df['price'] = df['ticker'].apply(lambda x: getPrice(x))
    df['Total'] = df['price']*df['count']
    df['cost basis'] = df['count'] * df['unit_cost']
    df['Profit / Loss'] = df['Total'] - df['cost basis']
    df['return'] = (df['price']/df['unit_cost'] - 1)*100
    df['PME_unit_cost'] = df['acq_date'].apply(lambda x: getSP500Unit(x))
    df['PME_shares'] = df['cost basis'] / df['PME_unit_cost']
    df['PME_comp_date'] = datetime.today() - timedelta(days=1)
    df['PME_current_price'] = df['PME_comp_date'].apply(lambda x: sp500_Current(x))
    df["PME_value"] = df['PME_current_price'] * df['PME_shares']
    # df1['PME_return'] = (df1['PME_current_price']/df1['PME_unit_cost'] - 1)*100
    df['$ Difference'] = df['Total'] - df['PME_value']

    return df




def detail(request, pk):
    qs = Portfolio.objects.filter(id = pk)
    qs1 = Stock.objects.filter(portfolio_id = pk)
    tickers= Stock.objects.filter(portfolio_id = pk).values_list('ticker')
    tick = []
    for i in tickers:
        # tick.extend(i.strip('()'))
        tick.append(i[0])

    tick.append('^GSPC')

    stocks_start = "2013-1-1"
    stocks_end = "2018-12-31"
    start_date = dateutil.parser.parse(stocks_start).date()
    end_date = dateutil.parser.parse(stocks_end).date()


    df1 = get_Port_Total(pk)

    portfolio_value = df1['Total'].sum()

    cost = df1['cost basis'].sum()

    profit_loss = portfolio_value - cost




    pme_value = df1['PME_value'].sum()
    ret_diff = df1['cost basis']/df1['Total']-1
    val_diff = portfolio_value - pme_value

    PME_df = df1.drop(columns=["return","PME_shares", "PME_comp_date", "PME_unit_cost", "PME_current_price", "count", "unit_cost", "acq_date",
                                    "price", "cost basis"])

    df_port = df1.drop(columns=["count","price", "unit_cost", "cost basis","acq_date", "return", "PME_unit_cost", "PME_shares", "PME_comp_date",
                                "PME_current_price", "PME_value",  "$ Difference","Profit / Loss"])
    print(df_port.info())

    df_port.set_index('ticker', inplace=True)

    title= qs[0]



    df = yf.download(tick, start=start_date, end=end_date)
    df_portindex = df.copy()
    df_sp500 = df['Close','^GSPC'].to_frame()
    df_sp500.columns = df_sp500.columns.droplevel()
    df_sp500.columns = ['SP 500']
    # print(df_sp500.head())

    df.drop(columns=['Open', 'High', 'Low', 'Volume', 'Close'], inplace=True)

    # weights = df["Adj Close"].div(df["Adj Close"].sum(axis = 1), axis = "index")

    # df_re = df.resample("A").last()
    df_re = df

    df_re.columns = df_re.columns.droplevel()

    #sp500 historical data for PME analysis
    # sp500 = yf.download("^GSPC", start=start_date, end=end_date)
    # sp500.drop(columns=['Open', 'High', 'Low', 'Volume', 'Close'], inplace=True)

    # sp_500 = sp_500_histdata.resample("A").last()
    # sp500m = sp500.resample("M").last()
    # # sp_500['TSLA'] = df_re['Adj Close']
    # df_re['SP_500'] = sp500m['Adj Close']


    ret = df_re.pct_change().dropna()

    summary = ann_risk_return(ret)
# Sharp Ratio
    risk_free_return = 0.017
    risk_free_risk = 0
    rf = [risk_free_return, risk_free_risk]
    summary["Sharpe"] = (summary["Return"].sub(rf[0]))/summary["Risk"]
#Total risk variance
    summary["TotalRisk_var"] = np.power(summary.Risk, 2)
#Cov matrix
    COV = ret.cov()*252
    summary["SystRisk_var"] = COV.iloc[:, -1]
    summary["UnsystRisk_var"] = summary["TotalRisk_var"].sub(summary["SystRisk_var"])
#Calc. beta
    summary["Beta"] = summary.SystRisk_var / summary.loc["^GSPC", "SystRisk_var"]

#calc capm
    summary["Capm_ret"] = rf[0] + (summary.loc["^GSPC", "Return"] - rf[0]) * summary.Beta
#calc alpha
    summary["Alpha"] = summary.Return - summary.Capm_ret

    summ_table = summary.drop(columns=['TotalRisk_var', 'SystRisk_var', 'UnsystRisk_var', 'Capm_ret'])


#Create index from Portfolio
    df_portindex.drop(columns=['Open', 'High', 'Low', 'Volume'],inplace=True)
    df_portindex.drop(('Close', '^GSPC'), axis = 1, inplace = True)
    df_portindex.drop(('Adj Close', '^GSPC'), axis = 1, inplace = True)
    weights = df_portindex.Close.div(df_portindex.Close.sum(axis = 1), axis = "index")
    returns = df_portindex["Adj Close"].pct_change().dropna()


    sp500_returns = df_sp500["SP 500"].pct_change().dropna()
    an_sp500_returns = sp500_returns.resample("A").last().to_frame()
    an_sp500_returns.index = an_sp500_returns.index.strftime("%Y-%d-%m")
    # print(an_sp500_returns)


    port_index = returns.mul(weights.shift().dropna()).sum(axis = 1).add(1).cumprod().mul(100)
    port_index[pd.to_datetime("2013-01-03")] = 100
    port_index.sort_index(inplace = True)

    # annual = port_index.resample("A", kind = "period").last().to_frame()
    annual = port_index.resample("A").last().to_frame()
    annual.index = annual.index.strftime("%Y-%d-%m")
    annual.columns = ["Price"]
    annual["Portfolio Return"] = np.log(annual.Price / annual.Price.shift())
    annual.dropna(inplace = True)
    # print(annual)
    annual['SP 500 Returns'] = an_sp500_returns['SP 500']
    annual.drop(columns=['Price'],inplace=True)


    # chart = pandas_highcharts.core.serialize(port_index, chart_type="stock", render_to='my-chart', output_type='json')
    # port_index_chart = pandas_highcharts.core.serialize(port_index, kind="line", render_to='my-port_index_chart', output_type='json')
    ann_chart = pandas_highcharts.core.serialize(annual, kind= "bar", title='Annualized return', render_to='ann-chart', output_type='json')
    port_chart = pandas_highcharts.core.serialize(df_port, kind="pie", title="Portfolio percentages", tooltip={'pointFormat': '{series.Ticker}: <b>{point.percentage:.1f}%</b>'}, render_to='port-chart', output_type='json')
    sp_500_table =  df_re.to_html(classes='table table-hover table-bordered table-striped')
    # ticker = PME_df.to_html(classes='table table-hover table-bordered table-striped', index_names=False)
    ticker = (
        PME_df.style
        .applymap(color_negative_red, subset=['$ Difference', 'Profit / Loss'])
        .set_table_attributes('class="table table-hover table-bordered table-striped"')
        .format({'Total': "{:,.2f}"})
        .format({'PME_value': "{:,.2f}"})
        .format({'$ Difference': "{:,.2f}"})
        .render()
            )
    html = (
        summ_table.style
        .applymap(color_negative_red, subset=['Alpha', 'Beta', 'Sharpe'])
        .set_table_attributes('class="table table-hover table-bordered table-striped"')
        .format({'Return': "{:.2%}"})
        .format({'Risk': "{:.2%}"})
        .format({'Alpha': "{:.2f}"})
        .format({'Beta': "{:.2f}"})
        .format({'Sharpe': "{:.2f}"})
        .render()
            )
    # summ_table = summary.to_html(classes='table table-hover table-bordered table-striped', index_names=False)
    annual_table = (
            annual.style
            .applymap(color_negative_red, subset=['Portfolio Return','SP 500 Returns'])
            .set_table_attributes('class="table table-hover table-bordered table-striped"')
            .format({'Portfolio Return': "{:.2%}"})
            .format({'SP 500 Returns': "{:.2%}"})
            .render()
            )

    # annual_table = annual.to_html(classes='table table-hover table-bordered table-striped', index_names=False)
    return render(request, 'detail.html',{"profit_loss":profit_loss,"html":html, "ann_chart":ann_chart, "annual_table":annual_table, "val_diff":val_diff,
                    "pme_value":pme_value,"port_chart":port_chart, "title":title,  "ticker":ticker, "portfolio_value":portfolio_value, "sp_500_table":sp_500_table})



def priceLookup(request, pk):
    import json
    port = Portfolio.objects.get(pk=pk)
    ticker =  port.stock.ticker
    api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ ticker +"/quote?token=pk_5a6bfc8f3d3d405f910aec024cc2bc14")

    try:
        api = json.loads(api_request.content)


    except Exception as e:
        api = "Error...."

    return render(request, 'detail_portfolio.html', {'api' : api, "ticker":ticker, "api_request":api_request})




class UpdatePortfolio(LoginRequiredMixin, generic.UpdateView):
    model = Portfolio
    template_name = 'update_portfolio.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        portfolio = super(UpdatePortfolio, self).get_object()
        if not portfolio.user == self.request.user:
            raise Http404
        return portfolio

class DeletePortfolio(LoginRequiredMixin, generic.DeleteView):
    model = Portfolio
    template_name = 'delete_portfolio.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        portfolio = super(DeletePortfolio, self).get_object()
        if not portfolio.user == self.request.user:
            raise Http404
        return portfolio

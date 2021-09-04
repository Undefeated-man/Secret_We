import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from django import forms

from login.models import LoginUser
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid, Page, Pie, Radar, Scatter
from pyecharts.commons.utils import JsCode

# Create your views here.
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


def check_list(request):
    # to ensure the user is login
    try:
        uid = request.get_signed_cookie(key="isLogin", salt="20200809")
    except:
        return redirect('/login/')
    try:
        status = request.get_signed_cookie(key="isLogin", salt="20200809")
        if (status != uid) and (uid != None):
            return redirect('/login/')
    except:
        return redirect('/login/')
    
    return render(request, "checklist.html")


def show_result(request):
    # to ensure the user is login
    try:
        uid = request.get_signed_cookie(key="isLogin", salt="20200809")
    except:
        return redirect('/login/')
    try:
        status = request.get_signed_cookie(key="isLogin", salt="20200809")
        if (status != uid) and (uid != None):
            return redirect('/login/')
    except:
        return redirect('/login/')
    if request.method == "GET":
        return render(request, "demo.html")


def download(request, name="demo.html"):
    # do something...
    def down_chunk_file_manager(file_path, chuck_size=1024):
        with open(file_path, "rb") as file:
            while True:
                chuck_stream = file.read(chuck_size)
                if chuck_stream:
                    yield chuck_stream
                else:
                    break

    file_path = "./templates/%s"%name
    response = StreamingHttpResponse(down_chunk_file_manager(file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(name)

    return response


def visualize(request):
    # to ensure the user is login
    try:
        uid = request.get_signed_cookie(key="isLogin", salt="20200809")
    except:
        return redirect('/login/')
    try:
        status = request.get_signed_cookie(key="isLogin", salt="20200809")
        if (status != uid) and (uid != None):
            return redirect('/login/')
    except:
        return redirect('/login/')

    
    if request.method == "GET":
        return render(request, "Visualization.html")
    elif request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        result = False
        if form.is_valid():
            f = request.FILES['file']
            with open('./demo.csv', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            title = request.POST.get("title", "")
            subtitle = request.POST.get("subtitle", "")
            type_ = request.POST.get("type", "")
            down = request.POST.get("down", "")
            df = pd.read_csv("demo.csv", index_col=0)
            if type_ == "bar":
                result = fansy_bar(df, title)
                if down:
                    return download(request, "demo.html")
            elif type_ == "pie":
                result = fansy_pie(df, title)
                if down:
                    return download(request, "demo.html")
            elif type_ == "pair":
                result = pairplot(df)
                if result:
                    return download(request, name="demo.png")
            elif type_ == "line":
                result = fansy_line(df, title)
                if down:
                    return download(request, "demo.html")
            elif type_ == "line-sim":
                result = sim_line(df, title, subtitle)
                if down:
                    return download(request, "demo.html")
            elif type_ == "scatter":
                result = fansy_scatter(df, title)
                if down:
                    return download(request, "demo.html")
            elif type_ == "heatmap":
                result = heatmap(df, title)
                if result:
                    return download(request, name="demo.png")
        if result:
            return redirect("/tools/visual/result")
        return HttpResponse("Something wrong with your input~ Please check whether you're missing some value required.")


def fansy_bar(df, title=""):
    try:
        col_name = df.columns
        y = list(df[col_name[-1]])
        y_name = col_name[-1]
        page = Page()
        if len(col_name) == 1:
            page.add(
                Bar()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(y_name, y)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        elif len(col_name) == 2:
            y1 = list(df[col_name[-2]])
            y1_name = col_name[-2]
            page.add(
                Bar()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(y_name, y)
                .add_yaxis(y1_name, y1)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        elif len(col_name) == 3:
            y1 = list(df[col_name[-2]])
            y1_name = col_name[-2]
            y2 = list(df[col_name[-3]])
            y2_name = col_name[-3]
            page.add(
                Bar()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(y_name, y)
                .add_yaxis(y1_name, y1)
                .add_yaxis(y2_name, y2)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        elif len(col_name) == 4:
            y1 = list(df[col_name[-2]])
            y1_name = col_name[-2]
            y2 = list(df[col_name[-3]])
            y2_name = col_name[-3]
            y3 = list(df[col_name[-4]])
            y3_name = col_name[-4]
            page.add(
                Bar()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(y_name, y)
                .add_yaxis(y1_name, y1)
                .add_yaxis(y2_name, y2)
                .add_yaxis(y3_name, y3)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        page.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False


def fansy_scatter(df, title=""):
    try:
        col_name = df.columns
        if len(col_name) == 1:
            c = (
                Scatter()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(col_name[-1], list(df[col_name[-1]]))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    visualmap_opts=opts.VisualMapOpts(),
                )
                .render("./templates/demo.html")
            )
        elif len(col_name) == 2:
            c = (
                Scatter()
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(col_name[-1], list(df[col_name[-1]]))
                .add_yaxis(col_name[-2], list(df[col_name[-2]]))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    visualmap_opts=opts.VisualMapOpts(),
                )
                .render("./templates/demo.html")
            )
        return True
    except Exception as e:
        print(e)
        return False


def pairplot(df):
    try:
        plt.figure(figsize = (15, 10))
        g = sns.pairplot(pd.DataFrame(df), diag_kind="kde",
                     plot_kws=dict(s=10, alpha=0.6))
        """for ax in g.axes.flatten():
            ax.set_ylabel(ax.get_ylabel(), rotation = 60)"""
        plt.savefig("./templates/demo.png")
        return True
    except Exception as e:
        print(e)
        return False


def sim_line(df, title="", subtitle=""):
    try:
        col_name = df.columns
        l = Line().add_xaxis(xaxis_data=[str(df.index[i]) for i in range(len(df))])
        for i in range(len(col_name)):
            l.add_yaxis(
                series_name=col_name[i],
                y_axis=df[col_name[i]],
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="max"),
                        opts.MarkPointItem(type_="min", name="min"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="avg")]
                ),
            )
        l.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            datazoom_opts=[opts.DataZoomOpts()],
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        l.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False

def fansy_line(df, title=""):
    try:
        col_name = df.columns
        background_color_js = (
            "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
            "[{offset: 0, color: '#c86589'}, {offset: 1, color: '#06a7ff'}], false)"
        )
        area_color_js = (
            "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
            "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
        )
        if len(col_name) == 1:
            c = (
                Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(
                    series_name=col_name[-1],
                    y_axis=df[col_name[-1]],
                    is_smooth=True,
                    is_symbol_show=True,
                    symbol="circle",
                    symbol_size=6,
                    linestyle_opts=opts.LineStyleOpts(color="#ebec99"),
                    label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
                    itemstyle_opts=opts.ItemStyleOpts(
                        color="red", border_color="#fff", border_width=3
                    ),
                    tooltip_opts=opts.TooltipOpts(is_show=False),
                    areastyle_opts=opts.AreaStyleOpts(color=JsCode(area_color_js), opacity=0.5),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title=title,
                        pos_bottom="5%",
                        pos_left="center",
                        title_textstyle_opts=opts.TextStyleOpts(color="#fff", font_size=16),
                    ),
                    xaxis_opts=opts.AxisOpts(
                        type_="category",
                        boundary_gap=False,
                        axislabel_opts=opts.LabelOpts(margin=30, color="#ffffff63"),
                        axisline_opts=opts.AxisLineOpts(is_show=False),
                        axistick_opts=opts.AxisTickOpts(
                            is_show=True,
                            length=25,
                            linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                        ),
                    ),
                    yaxis_opts=opts.AxisOpts(
                        type_="value",
                        position="right",
                        axislabel_opts=opts.LabelOpts(margin=20, color="#ffffff63"),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(width=2, color="#fff")
                        ),
                        axistick_opts=opts.AxisTickOpts(
                            is_show=True,
                            length=15,
                            linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                        ),
                    ),
                    legend_opts=opts.LegendOpts(is_show=True, pos_bottom=20, pos_left=10),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        elif len(col_name) == 2:
            c = (
                Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
                .add_xaxis([str(df.index[i]) for i in range(len(df))])
                .add_yaxis(
                    series_name=col_name[-1],
                    y_axis=df[col_name[-1]],
                    is_smooth=True,
                    is_symbol_show=True,
                    symbol="circle",
                    symbol_size=6,
                    linestyle_opts=opts.LineStyleOpts(color="#ebec99"),
                    label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
                    itemstyle_opts=opts.ItemStyleOpts(
                        color="red", border_color="#fff", border_width=3
                    ),
                    tooltip_opts=opts.TooltipOpts(is_show=False),
                    areastyle_opts=opts.AreaStyleOpts(color=JsCode(area_color_js), opacity=0.5),
                )
                .add_yaxis(
                    series_name=col_name[-2],
                    y_axis=df[col_name[-2]],
                    is_smooth=True,
                    is_symbol_show=True,
                    symbol="circle",
                    symbol_size=6,
                    linestyle_opts=opts.LineStyleOpts(color="#fff"),
                    label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
                    itemstyle_opts=opts.ItemStyleOpts(
                        color="blue", border_color="#fff", border_width=3
                    ),
                    tooltip_opts=opts.TooltipOpts(is_show=False),
                    areastyle_opts=opts.AreaStyleOpts(color=JsCode(area_color_js), opacity=0.5),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title=title,
                        pos_bottom="5%",
                        pos_left="center",
                        title_textstyle_opts=opts.TextStyleOpts(color="#fff", font_size=16),
                    ),
                    xaxis_opts=opts.AxisOpts(
                        type_="category",
                        boundary_gap=False,
                        axislabel_opts=opts.LabelOpts(margin=30, color="#ffffff63"),
                        axisline_opts=opts.AxisLineOpts(is_show=False),
                        axistick_opts=opts.AxisTickOpts(
                            is_show=True,
                            length=25,
                            linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                        ),
                    ),
                    yaxis_opts=opts.AxisOpts(
                        type_="value",
                        position="right",
                        axislabel_opts=opts.LabelOpts(margin=20, color="#ffffff63"),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(width=2, color="#fff")
                        ),
                        axistick_opts=opts.AxisTickOpts(
                            is_show=True,
                            length=15,
                            linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                        ),
                    ),
                    legend_opts=opts.LegendOpts(is_show=True, pos_bottom=20, pos_left=10),
                    datazoom_opts=[opts.DataZoomOpts()],
                )
            )
        (
            Grid(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
            .add(
                c,
                grid_opts=opts.GridOpts(
                    pos_top="20%",
                    pos_left="10%",
                    pos_right="10%",
                    pos_bottom="15%",
                    is_contain_label=True,
                ),
            )
            .render("./templates/demo.html")
        )
        return True
    except Exception as e:
        print(e)
        return False


def heatmap(df, title=""):
    try:
        corr = df.corr()
        plt.figure(figsize = (15, 10))
        sns.heatmap(corr, cmap='RdBu', linewidths = 0.05).set(title=title)
        plt.savefig("./templates/demo.png")
        return True
    except Exception as e:
        print(e)
        return False


def fansy_pie(df, title=""):
    try:    
        col_name = df.columns
        page = Page()
        for i in range(len(col_name)):
            y = list(df[col_name[i]])
            y_name = col_name[i]
            page.add(
                Pie()
                .add(
                    "",
                    [list(z) for z in zip([str(df.index[i]) for i in range(len(df))], y)],
                    label_opts=opts.LabelOpts(is_show=True, type_ = 'scroll'),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title)
                )
            )
        page.render("./templates/demo.html")
        
        return True
    except Exception as e:
        print(e)
        return False

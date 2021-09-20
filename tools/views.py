import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from django import forms

from sklearn.manifold import TSNE
from sklearn import decomposition
from login.models import LoginUser
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid, Page, Pie, Radar, Scatter, Boxplot
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


def dimension(request):
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
        return render(request, "dimension.html")
    elif request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        result = False
        print(form)
        if form.is_valid():
            f = request.FILES['file']
            with open('./demo.csv', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            title = request.POST.get("title_", "")
            subtitle = request.POST.get("subtitle", "")
            type_ = request.POST.get("type", "")
            down = request.POST.get("down", "")
            x_axis_name = request.POST.get("x_axis_name", "")
            y_axis_name = request.POST.get("y_axis_name", "")
            df = pd.read_csv("demo.csv", index_col=0)
            if type_ == "pca":
                result = pca_analysis(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, name="pca.csv")
            elif type_ == "tsne":
                result = tsne(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, "tsne.csv")
                else:
                    return download(request, "demo.png")
            
        if result:
            return redirect("/tools/visual/result")
        return HttpResponse("Something wrong with your input~ Please check whether you're missing some value required(For example: your title).")



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
            x_axis_name = request.POST.get("x_axis_name", "")
            y_axis_name = request.POST.get("y_axis_name", "")
            high = request.POST.get("high-level", "")
            df = pd.read_csv("demo.csv", index_col=0)
            if type_ == "bar":
                result = fansy_bar(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, "demo.html")
            elif type_ == "pie":
                result = fansy_pie(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, "demo.html")
            elif type_ == "pair":
                result = pairplot(df)
                if result:
                    return download(request, name="demo.png")
            elif type_ == "line":
                result = fansy_line(df, title, x_axis_name, y_axis_name)
                if result == -1:
                    return HttpResponse("Only allow draw lines with data within 2 columns.")
                if down:
                    return download(request, "demo.html")
            elif type_ == "line-sim":
                result = sim_line(df, title, subtitle, x_axis_name, y_axis_name, high)
                if down:
                    return download(request, "demo.html")
            elif type_ == "scatter":
                result = fansy_scatter(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, "demo.html")
            elif type_ == "heatmap":
                result = heatmap(df, title)
                if result:
                    return download(request, name="demo.png")
            elif type_ == "boxplot":
                result = boxplot(df, title, subtitle, x_axis_name, y_axis_name)
                if down:
                    return download(request, name="demo.html")
            
        if result:
            return redirect("/tools/visual/result")
        return HttpResponse("Something wrong with your input~ Please check whether you're missing some value required(For example: your title).")


def tsne(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
    try:
        t = TSNE()
        x = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        X_embedded = t.fit_transform(x)
        pd.DataFrame(X_embedded, columns=["x", "y"]).to_csv("./templates/tsne.csv")

        # solve the Chinese encoding problem
        plt.rcParams["font.sans-serif"] = ["simhei"]
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像负号显示为方块问题
        sns.set(font='simhei', font_scale=1.5)

        plt.figure(figsize = (15, 10))
        g = sns.scatterplot(X_embedded[:, 0], X_embedded[:, 1], hue=y, legend='full', s=75)
        """for ax in g.axes.flatten():
            ax.set_ylabel(ax.get_ylabel(), rotation = 60)"""
        plt.savefig("./templates/demo.png")
        return True
    except Exception as e:
        print(e)
        return False


def pca_analysis(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
    try:
        pca = decomposition.PCA()
        pca.fit(df)
        X_pca = pca.fit_transform(df)
        X_pca = pd.DataFrame(X_pca, columns=["PC%d"%(i+1) for i in range(X_pca.shape[1])])
        X_pca.to_csv("./templates/pca.csv")

        # visualize the pca result
        ratio = list(pca.explained_variance_ratio_)
        eigen_vector = [list(np.abs(i)) for i in pca.components_][:10]
        page = Page()
        page.add(
            Pie()
            .add(
                "",
                [list(z) for z in zip(["PC%d"%(i+1) for i in range(10)], list(ratio))],
                label_opts=opts.LabelOpts(is_show=True),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
                legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
                xaxis_opts=opts.AxisOpts(name=x_axis_name),
                yaxis_opts=opts.AxisOpts(name=y_axis_name),
            ),

            Bar()
            .add_xaxis(["PC%d"%(i+1) for i in range(10)])
            .add_yaxis("", ratio)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
                legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
                xaxis_opts=opts.AxisOpts(name='Principle\nComponents'),
                yaxis_opts=opts.AxisOpts(name=y_axis_name),
                datazoom_opts=[opts.DataZoomOpts()],
            ),
        )
        page.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False


def boxplot(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
    try:
        col_name = df.columns
        xaxis_data = [str(col_name[i]) for i in range(len(col_name))]
        box_plot = Boxplot().add_xaxis(xaxis_data=xaxis_data)
        y_data = []
        for i in range(len(col_name)):
            y_data.append(list(df[col_name[i]]))
        box_plot.add_yaxis("", box_plot.prepare_data(y_data))
        box_plot.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=True,
                axislabel_opts=opts.LabelOpts(
                    interval=0,
                    rotate= 25,
                ),
                splitarea_opts=opts.SplitAreaOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
        )
        scatter = (
            Scatter()
            .add_xaxis(xaxis_data=xaxis_data)
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    is_show=False,
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                ),
            )
        )
        for i in range(len(df)):
            scatter.add_yaxis(series_name="", y_axis=list(df.iloc[i, :]), symbol_size=10)

        grid = (
            Grid(opts.InitOpts(height="500px"))
            .add(
                box_plot,
                grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="25%"),
            )
            .add(
                scatter,
                grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="25%"),
            )
            .render("./templates/demo.html")
        )
        
        return True
    except Exception as e:
        print(e)
        return False


def fansy_bar(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
    try:
        col_name = df.columns
        b = Bar().add_xaxis([str(df.index[i]) for i in range(len(df))])
        for i in range(len(col_name)):
                b.add_yaxis(col_name[i], list(df[col_name[i]]))
        b.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
            legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
            xaxis_opts=opts.AxisOpts(name=x_axis_name),
            yaxis_opts=opts.AxisOpts(name=y_axis_name),
            datazoom_opts=[opts.DataZoomOpts()],
        )
        b.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False


def fansy_scatter(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
    try:
        col_name = df.columns
        s = Scatter().add_xaxis([str(df.index[i]) for i in range(len(df))])
        if len(df) < 20:
            for i in range(len(col_name)):
                s.add_yaxis(col_name[i], list(df[col_name[i]]))
        else:
            for i in range(len(col_name)):
                s.add_yaxis(col_name[i], list(df[col_name[i]]), symbol_size=2.5, label_opts=opts.LabelOpts(is_show=False))
        s.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
            legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
            #visualmap_opts=opts.VisualMapOpts(),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True), name=x_axis_name),
            yaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True), name=y_axis_name),
            datazoom_opts=[opts.DataZoomOpts()],
        )
        s.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False


def pairplot(df):
    try:
        # solve the Chinese encoding problem
        plt.rcParams["font.sans-serif"] = ["simhei"]
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像负号显示为方块问题
        sns.set(font='simhei', font_scale=1.5)
        
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


def sim_line(df, title="", subtitle="", x_axis_name="", y_axis_name="", high=False):
    try:
        col_name = df.columns
        l = Line().add_xaxis(xaxis_data=[str(df.index[i]) for i in range(len(df))])
        for i in range(len(col_name)):
            l.add_yaxis(
                series_name=col_name[i],
                y_axis=df[col_name[i]],
                #markpoint_opts=opts.MarkPointOpts(
                #    data=[
                #        opts.MarkPointItem(type_="max", name="max"),
                #        opts.MarkPointItem(type_="min", name="min"),
                #    ]
                #),
                #markline_opts=opts.MarkLineOpts(
                #    data=[opts.MarkLineItem(type_="average", name="avg")]
                #),
            )
        if high:
            l.set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
                legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                datazoom_opts=[opts.DataZoomOpts()],
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False, name=x_axis_name),
                yaxis_opts=opts.AxisOpts(name=y_axis_name),
            )
        else:
            l.set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
                legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
                datazoom_opts=[opts.DataZoomOpts()],
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False, name=x_axis_name),
                yaxis_opts=opts.AxisOpts(name=y_axis_name),
            )
        l.render("./templates/demo.html")
        return True
    except Exception as e:
        print(e)
        return False


def fansy_line(df, title="", x_axis_name="", y_axis_name=""):
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
                        name=x_axis_name,
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
                        name=y_axis_name,
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
                        name=x_axis_name,
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
                        name=y_axis_name,
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
        if len(col_name) > 2:
            return -1
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
        # solve the Chinese encoding problem
        plt.rcParams["font.sans-serif"] = ["simhei"]
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像负号显示为方块问题
        sns.set(font='simhei', font_scale=1.5)
        
        max_title = 0
        corr = df.corr()
        all_alpha = True
        for i in df.columns:
            if len(i) > max_title:
                max_title = len(i)
                for j in i:
                    if not (ord(j)>64 and ord(j)<91) and (ord(j)>96 and ord(j)<123):
                        all_alpha = False
        if (max_title > 9 and not all_alpha) or (max_title > 18 and all_alpha):
            plt.figure(figsize = (35, 30))
            sns.heatmap(corr, annot=True, cmap='RdBu', linewidths = 0.05, annot_kws={"size":30}).set_title(label=title, fontdict = {'fontsize': 45})
        else:
            plt.figure(figsize = (20, 15))
            sns.heatmap(corr, annot=True, cmap='RdBu', linewidths = 0.05).set(title=title)
        plt.savefig("./templates/demo.png")
        return True
    except Exception as e:
        print(e)
        return False


def fansy_pie(df, title="", subtitle="", x_axis_name="", y_axis_name=""):
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
                    label_opts=opts.LabelOpts(is_show=True),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
                    legend_opts = opts.LegendOpts(type_="scroll", orient="vertical", pos_right="2%"),
                    xaxis_opts=opts.AxisOpts(name=x_axis_name),
                    yaxis_opts=opts.AxisOpts(name=y_axis_name),
                )
            )
        page.render("./templates/demo.html")
        
        return True
    except Exception as e:
        print(e)
        return False


def examples(request):
    return render(request, "example.html")
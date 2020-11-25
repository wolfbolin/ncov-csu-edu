<template>
    <div class="wb-about">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>关于该服务的其他事情</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <div class="userChart" id="userChart" ref="userChart"></div>
            <div class="signChart" id="signChart" ref="signChart"></div>
            <div class="tips">
                <h2>开发者</h2>
                <p>WolfBolin<br/>
                    可以选择以下方式联系我<br/>
                    我的主页：<a href="https://wolfbolin.com" target="_blank">https://wolfbolin.com</a><br/>
                    我的博客：<a href="https://blog.wolfbolin.com" target="_blank">https://blog.wolfbolin.com</a><br/>
                    我的E-Mail：<a href="mailto:mailto@wolfbolin.com" target="_blank">mailto@wolfbolin.com</a><br/>
                    我的Github：<a href="https://github.com/wolfbolin" target="_blank">WolfBolin Github</a><br/>
                    我的BiliBili：<a href="https://space.bilibili.com/72835041" target="_blank">WolfBolin BiliBili</a>
                </p>
                <h2>项目贡献者</h2>
                <p><a href="https://github.com/kongmoumou" target="_blank">kongmoumou Github</a><br/>
                </p>
                <h2>未完待续</h2>
                <p>最后更新时间<br/>
                    2020-10-16 23:30
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'List',
    data() {
        return {
            userChart: null,
            userChartOpt: {},
            userChartKey: [],
            userChartVal: [],
            signChart: null,
            signChartOpt: {},
            signChartDate: [],
            signChartData: [],
            signChartRange: [],
        }
    },
    methods: {
        initChart: function () {
            let userChartWidth = this.$refs.userChart.clientWidth
            let userChartDom = document.getElementById('userChart')
            userChartDom.style.height = userChartWidth * 0.6 + "px"
            this.userChart = this.$echarts.init(userChartDom);
            this.userChartOpt = {
                title: {
                    text: '30日内用户总量曲线图',
                    left: 'center',
                    textStyle: {
                        fontSize: 28
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: {
                            backgroundColor: '#6a7985'
                        }
                    }
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: []
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    data: [],
                    type: 'line',
                    areaStyle: {
                        normal: {
                            color: '#91BEF0' //改变区域颜色
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: '#91BEF0', //改变折线点的颜色
                            lineStyle: {
                                color: '#91BEF0' //改变折线颜色
                            }
                        }
                    },
                }]
            };

            let signChartWidth = this.$refs.signChart.clientWidth
            let signChartDom = document.getElementById('signChart')
            signChartDom.style.height = signChartWidth * 0.9 + "px"
            this.signChart = this.$echarts.init(signChartDom);
            this.signChartOpt = {
                title: {
                    text: '7日内自动打卡时刻图',
                    left: 'center',
                    textStyle: {
                        fontSize: 28
                    }
                },
                visualMap: {
                    max: 3000,
                    inRange: {
                        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
                    }
                },
                xAxis3D: {
                    type: 'category',
                    data: []
                },
                yAxis3D: {
                    type: 'category',
                    data: []
                },
                zAxis3D: {
                    type: 'value'
                },
                grid3D: {
                    viewControl: {
                        distance: 200,
                        zoomSensitivity: 1,
                        rotateSensitivity: 5,
                    },
                    boxWidth: 100,
                    boxDepth: 80,
                    light: {
                        main: {
                            intensity: 1.2
                        },
                        ambient: {
                            intensity: 0.3
                        }
                    }
                },
                series: [{
                    type: 'bar3D',
                    data: [],
                    shading: 'lambert',
                    label: {
                        show: false,
                        textStyle: {
                            fontSize: 16,
                            borderWidth: 1
                        }
                    },
                    itemStyle: {
                        opacity: 1
                    },
                    emphasis: {
                        label: {
                            textStyle: {
                                fontSize: 20,
                                color: '#900'
                            }
                        },
                        itemStyle: {
                            color: '#900'
                        }
                    }
                }]
            }
        },
        updateChart: function () {
            // 获取数据
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/user/count`)
                .then(function (res) {
                    console.log(res)
                    if (res.data.status === 'success') {
                        console.log(res.data["user_data"])
                        that.userChartOpt.xAxis.data = res.data["user_data"][0]
                        that.userChartOpt.series[0].data = res.data["user_data"][1]
                        that.userChart.setOption(that.userChartOpt)
                        that.signChartOpt.xAxis3D.data = res.data["sign_data"][0]
                        that.signChartOpt.yAxis3D.data = res.data["sign_data"][1]
                        console.log(that.signChartOpt.series)
                        that.signChartOpt.series[0].data = res.data["sign_data"][2]
                        that.signChart.setOption(that.signChartOpt)
                    } else {
                        that.$message({
                            message: "res.data.message",
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    console.log(res);
                })
        }
    },
    mounted() {
        this.initChart();
        this.updateChart();
    }
}
</script>

<style lang="scss" scoped>
.wb-about {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
    }

    .alert {
        width: 60%;
        margin: 0 auto;
    }

    .userChart {
        width: 100%;
        margin-top: 16px;
    }

    .signChart {
        width: 100%;
        margin-top: 16px;
    }

    .tips {
        margin-top: 36px;

        h2 {
            display: inline-block;
            padding: 4px;
            border-bottom: #91BEF0 3px solid;
        }

        p {
            font-size: 16px;
            line-height: 32px;
        }
    }
}
</style>

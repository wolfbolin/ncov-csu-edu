<template>
    <div class="chart">
        <div class="signChart" id="signChart" ref="signChart"></div>
    </div>
</template>

<script>
let echarts = require('echarts/lib/echarts');
require('echarts/lib/component/title');
require('echarts-gl');

export default {
    name: "sign_bar",
    data() {
        return {
            signChart: null,
            signChartOpt: {},
        }
    },
    methods: {
        initChart: function () {
            let signChartWidth = this.$refs.signChart.clientWidth
            let signChartDom = document.getElementById('signChart')
            signChartDom.style.height = signChartWidth * 0.8 + "px"
            this.signChart = echarts.init(signChartDom);
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
            this.$http.get(data_host + `/task/count/sign`)
                .then(function (res) {
                    if (res.data.status === 'success') {
                        that.signChartOpt.xAxis3D.data = res.data["sign_data"][0]
                        that.signChartOpt.yAxis3D.data = res.data["sign_data"][1]
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
        console.log("Load sign bar chart")
        this.initChart();
        this.updateChart();
    }
}
</script>

<style scoped>

</style>
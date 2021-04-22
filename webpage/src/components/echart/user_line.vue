<template>
    <div class="chart">
        <div class="userChart" id="userChart" ref="userChart"></div>
    </div>
</template>

<script>
let echarts = require('echarts/lib/echarts');
require('echarts/lib/chart/line');
require('echarts/lib/component/title');
require('echarts/lib/component/tooltip');
export default {
    name: "user_line",
    data() {
        return {
            userChart: null,
            userChartOpt: {},
        }
    },
    methods: {
        initChart: function () {
            let userChartWidth = this.$refs.userChart.clientWidth
            let userChartDom = document.getElementById('userChart')
            userChartDom.style.height = userChartWidth * 0.375 + "px"
            this.userChart = echarts.init(userChartDom);
            this.userChartOpt = {
                title: {
                    text: '30日内用户总量曲线图',
                    left: 'center',
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
        },
        updateChart: function () {
            // 获取数据
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/data/count/user`)
                .then(function (res) {
                    if (res.data.status === 'success') {
                        that.userChartOpt.xAxis.data = res.data["user_data"][0]
                        that.userChartOpt.series[0].data = res.data["user_data"][1]
                        that.userChart.setOption(that.userChartOpt)
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
        console.log("Load user line chart")
        this.initChart();
        this.updateChart();
    }

}
</script>

<style scoped>

</style>

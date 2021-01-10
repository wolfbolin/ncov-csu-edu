<template>
    <div class="chart">
        <div class="addrChart" id="addrChart" ref="addrChart"></div>
    </div>
</template>

<script>
let echarts = require('echarts/lib/echarts');
require('echarts/lib/chart/map');
require('echarts/lib/component/title');
require('echarts/lib/component/tooltip');
export default {
    name: "user_line",
    data() {
        return {
            geo: this.$store.state.geo,
            chart: null,
            chartOpt: {},
        }
    },
    methods: {
        initChart: function () {
            let chartWidth = this.$refs.addrChart.clientWidth
            let chartDom = document.getElementById('addrChart')
            chartDom.style.height = chartWidth + "px"
            this.chart = echarts.init(chartDom);
            this.chartOpt = {
                title: {
                    text: '香港18区人口密度 （2011）',
                    subtext: '人口密度数据来自Wikipedia',
                },
                series: [
                    {
                        name: '香港18区人口密度',
                        type: 'map',
                        map: 'CN'
                    }
                ]
            }
            this.chart.setOption(this.chartOpt)
            this.chart.on('click', function (params) {
                console.log(params)
            });
        },
        getGEOJson: async function (code) {
            let data_host = this.$store.state.host;
            let geo_data = await this.$http.get(data_host + `/geo/${code}`)
            if(geo_data.data["status"] === "success"){
                return geo_data.data
            }else{
                return null
            }
        }
    },
    mounted() {
        console.log("Load user line chart")
        this.initChart();
        this.getGEOJson();
        console.log(this.geo)
    }
}
</script>

<style scoped>

</style>
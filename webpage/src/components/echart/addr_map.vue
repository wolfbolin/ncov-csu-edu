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
            code_index: {"中国": 100000},
            update_date: "",
            register_map: [],
            location_tree: {},
            map_path_history: ["中国"],
            map_code_history: [100000],

        }
    },
    methods: {
        fetch_data: function () {
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/task/count/location`)
                .then(function (res) {
                    if (res.data.status === 'success') {
                        console.log("地图数据", res.data)
                        that.update_date = res.data.update_date
                        that.location_tree = res.data.data
                        that.update_map("中国", 100000, that.location_tree.child["中国"])
                    } else {
                        that.$message({
                            message: "未知错误",
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    console.log(res);
                })
        },
        click_map: function (params) {
            if (Object.prototype.hasOwnProperty.call(params, "target")) {
                if (params.target === undefined) {
                    // 点击空白区域
                    if (this.map_path_history.length <= 1) {
                        this.$message({
                            message: '不能再倒退啦',
                            type: 'warning'
                        });
                        return
                    }
                    this.map_backward()
                } else {
                    return; // 交给另一个事件处理
                }
            } else {
                if (this.map_path_history.length >= 3) {
                    this.$message({
                        message: '不能更详细啦',
                        type: 'warning'
                    });
                    return
                }
                this.map_forward(params.name)
            }
        },
        map_forward: function (name) {
            let data = this.location_tree
            for (let item of this.map_path_history) {
                data = data.child[item]
            }

            if (data.child[name] === undefined) {
                this.$message({
                    message: '没有更多数据啦',
                    type: 'warning'
                });
                return
            } else {
                data = data.child[name]
            }

            let code = this.code_index[name]
            this.map_path_history.push(name)
            this.map_code_history.push(code)
            this.update_map(name, code, data)
        },
        map_backward: function () {
            this.map_path_history.pop()
            this.map_code_history.pop()
            let name = "", code = ""
            let data = this.location_tree
            for (let i = 0; i < this.map_path_history.length; i++) {
                name = this.map_path_history[i]
                code = this.map_code_history[i]
                data = data.child[name]
            }
            this.update_map(name, code, data)
        },
        update_map: async function (name, code, data) {
            console.log("更新地图", name, code, data)
            // 更新地图时间
            this.chartOpt.title.subtext = `数据时间：${this.update_date}`

            // 获取地图数据
            let geo_data = await this.getGEOJson(code)
            console.log("地图数据", geo_data)
            if (geo_data === null) {
                this.$message({
                    message: `获取<${name}>地图失败`,
                    type: 'error'
                });
            }

            // 更新地图信息
            Object.assign(this.code_index, this.code_index, geo_data["code_index"])
            if (this.register_map.indexOf(name) === -1) {
                this.register_map.push(name)
                echarts.registerMap(name, geo_data) // 注册地图名称
            }
            this.chartOpt.series[0]["map"] = name  // 更新地图配置

            // 更新地图数据
            let map_data = []
            for (let item in data.child) {
                map_data.push({name: data.child[item].name, value: data.child[item].count})
            }
            this.chartOpt.series[0].data = map_data

            // 更新地图参数
            this.chart.setOption(this.chartOpt)
        },
        getGEOJson: async function (code) {
            let data_host = this.$store.state.host;
            let geo_data = await this.$http.get(data_host + `/geo/${code}`)
            console.log("地图数据", geo_data)
            if (geo_data.data["status"] === "success") {
                return geo_data.data
            } else {
                return null
            }
        },
        initChart: function () {
            let chartWidth = this.$refs.addrChart.clientWidth
            let chartDom = document.getElementById('addrChart')
            chartDom.style.height = chartWidth + "px"
            this.chart = echarts.init(chartDom);
            this.chartOpt = {
                title: {
                    text: '打卡用户分布图',
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}<br/>打卡人数：{c}'
                },
                visualMap: {
                    min: 0,
                    max: 5000,
                    text: ['High', 'Low'],
                    inRange: {
                        color: ['lightskyblue', 'yellow', 'orangered']
                    }
                },
                series: [
                    {
                        type: 'map',
                        map: '',
                        label: {
                            show: false,
                            textStyle: {
                                fontSize: 16,
                                borderWidth: 1
                            }
                        },
                        zoom: 1.25,
                        roam: true,
                        scaleLimit: {
                            min: 1,
                            max: 4
                        },
                    }
                ]
            }
            // this.chart.setOption(this.chartOpt)
            this.chart.on('click', this.click_map);
            this.chart.getZr().on('click', this.click_map);
        },
    },
    mounted() {
        console.log("Load user line chart")
        this.initChart();
        this.fetch_data();
    }
}
</script>

<style scoped>

</style>
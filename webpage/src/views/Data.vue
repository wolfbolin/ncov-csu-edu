<template>
    <div class="wb-data">
        <div class="inner">
            <img src="../assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>现共有{{ item_num }}位用户正在享用自动打卡服务</p>
            <div class="alert">
                <el-alert type="warning" center :closable="false">
                    <template slot="title">
                        服务反馈与通知群 {{this.$store.state.group}}
                    </template>
                </el-alert>
            </div>
            <el-table class="table" stripe
                      v-loading="loading" :data="dataTable">
                <el-table-column prop="username" label="账户"></el-table-column>
                <el-table-column prop="nickname" label="昵称"></el-table-column>
                <el-table-column prop="phone" label="电话"></el-table-column>
                <el-table-column prop="time" label="时间"></el-table-column>
            </el-table>
            <el-pagination
                background
                layout="prev, pager, next"
                :total="item_num"
                :page-size.sync="page_size"
                @current-change="pageChange"
                :current-page.sync="page_now">
            </el-pagination>
            <div class="chart">
                <component :is="user_line"></component>
                <component :is="addr_map"></component>
            </div>
        </div>
    </div>
</template>

<script>
import user_line from "@/components/echart/user_line";
import addr_map from "@/components/echart/addr_map";

export default {
    name: "Data",
    data() {
        return {
            user_line: user_line,
            addr_map: addr_map,
            loading: true,
            item_num: 0,
            page_now: 1,
            page_size: 25,
            dataTable: [],
        }
    },
    methods: {
        pageChange: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/user/list`,
                {
                    params: {
                        page_now: this.page_now,
                        page_size: this.page_size
                    }
                })
                .then(function (res) {
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.item_num = res.data.data["item_num"]
                        that.page_now = res.data.data["page_now"]
                        that.page_size = res.data.data["page_size"]
                        that.dataTable = res.data.data["user_list"]
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    console.log(res);
                })
        },
    },
    mounted() {
        this.pageChange();
    }
}
</script>

<style lang="scss" scoped>
.wb-data {
    .table {
        width: 90%;
        display: inline-block;
        margin-bottom: 16px;
    }
    .chart {
        margin-top: 36px;
    }
}
</style>

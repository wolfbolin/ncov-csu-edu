<template>
    <div class="wb-list">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>下列展示了使用该服务的用户信息</p>
            <el-table class="table" stripe style="width: 90%"
                      v-loading="loading" :data="tableData">
                <el-table-column
                    prop="username"
                    label="账户">
                </el-table-column>
                <el-table-column
                    prop="nickname"
                    label="昵称">
                </el-table-column>
                <el-table-column
                    prop="phone"
                    label="电话">
                </el-table-column>
                <el-table-column
                    prop="time"
                    label="时间">
                </el-table-column>
            </el-table>
            <div class="tips">
                <h2>阿巴阿巴</h2>
                <p>阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'List',
    data() {
        return {
            loading: true,
            tableData: [{
                username: "3901****21",
                nickname: "WolfBolin",
                phone: "155****8042",
                time: "01:00"
            }]
        }
    },
    methods: {
        get_user_list: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/user/list`)
                .then(function (res) {
                    console.log(res)
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.tableData = res.data.data
                    }
                })
                .catch(function (res) {
                    console.log(res);
                })
        }
    },
    mounted() {
        this.get_user_list()
    }
}
</script>

<style lang="scss" scoped>
.wb-list {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
    }

    .table {
        display: inline-block;
    }
}
</style>
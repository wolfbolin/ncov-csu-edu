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
                <h2>如何获取结果？</h2>
                <p>目前没办法<br/>
                    VIP用户可凭借短信了解<br/>
                    普通用户的打卡查询的代码还没写<br/>
                    你可以来补充<br/>
                    我累了
                </p>
                <h2>这真实吗？</h2>
                <p>是的<br/>
                    目前这是现有的用户<br/>
                    你可以在任何时候删除自己的账号<br/>
                    并在懒惰的时候添加<br/>
                    为啥要删？<br/>
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
                    }else{
                        that.$message({
                            message: res.data.message,
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
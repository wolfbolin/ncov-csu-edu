<template>
    <div class="wb-list">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>现共有{{ item_num }}位用户正在享用自动打卡服务</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <el-table class="table" stripe
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
            <el-pagination
                background
                layout="prev, pager, next"
                :total="item_num"
                :page-size.sync="page_size"
                @current-change="pageChange"
                :current-page.sync="page_now">
            </el-pagination>
            <div class="tips">
                <h2>如何获取结果？</h2>
                <p>目前没办法<br/>
                    VIP用户可凭借短信了解<br/>
                    普通用户的打卡查询的代码还没写<br/>
                    你有需要可以自己来补充<br/>
                    我累了我好困<br/>
                    我好困<br/>
                    好困<br/>
                    困
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
            item_num: 0,
            page_now: 1,
            page_size: 25,
            tableData: []
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
                }
            )
                .then(function (res) {
                    console.log(res)
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.item_num = res.data.data["item_num"]
                        that.page_now = res.data.data["page_now"]
                        that.page_size = res.data.data["page_size"]
                        that.tableData = res.data.data["user_list"]
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
        }
    },
    mounted() {
        this.pageChange()
    }
}
</script>

<style lang="scss" scoped>
.wb-list {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
    }

    .alert {
        width: 60%;
        margin: 0 auto;
    }

    .table {
        width: 90%;
        display: inline-block;
        margin-bottom: 16px;
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
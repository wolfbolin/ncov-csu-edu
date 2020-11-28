<template>
    <div class="wb-list">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>关于用户他自己的一些事情</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <el-row type="flex" :gutter="20">
                <el-col :span="16">
                    <el-form class="form" ref="form" label-position="left" label-width="60px"
                             v-loading="loading" :rules="rules" :model="formData">
                        <el-form-item label="账号" prop="username">
                            <el-input v-model="formData.username" placeholder="信息门户账户"></el-input>
                        </el-form-item>
                        <el-form-item label="手机" prop="phone">
                            <el-input v-model="formData.phone" placeholder="用于身份认证" show-password></el-input>
                        </el-form-item>
                        <el-button type="success" @click="check_form('get_task')" plain>查询任务</el-button>
                        <el-button type="danger" @click="check_form('del_task')" plain>删除任务</el-button>
                    </el-form>
                </el-col>
                <el-col :span="8" class="info">
                    <el-row class="item">
                        <el-col :span="12" class="key">
                            <p>用户昵称</p>
                        </el-col>
                        <el-col :span="12" class="val">
                            <p>{{ taskInfo.nickname }}</p>
                        </el-col>
                    </el-row>
                    <el-row class="item">
                        <el-col :span="12" class="key">
                            <p>打卡时间</p>
                        </el-col>
                        <el-col :span="12" class="val">
                            <p>{{ taskInfo.taskTime }}</p>
                        </el-col>
                    </el-row>
                    <el-row class="item">
                        <el-col :span="12" class="key">
                            <p>短信通知</p>
                        </el-col>
                        <el-col :span="12" class="val">
                            <p>{{ taskInfo.smsOpt }}</p>
                        </el-col>
                    </el-row>
                </el-col>
            </el-row>
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
                <h2>解除绑定</h2>
                <p>认真的？<br/>
                    这么实在的工具为何放弃？<br/>
                    信息填错重写登录即可覆盖现有信息<br/>
                    删除功能是做着玩的(能用)<br/>
                    你为啥要删除<br/>
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
            loading: false,
            formData: {
                username: "",
                phone: ""
            },
            taskInfo: {
                nickname: "",
                taskTime: "",
                smsOpt: ""
            },
            rules: {
                username: [
                    {required: true, message: '请输入信息门户账户', trigger: 'blur'},
                    {min: 8, max: 14, message: '长度在 8 到 14 个字符', trigger: 'blur'}
                ],
                phone: [
                    {required: true, message: '请输入收信电话号码', trigger: 'blur'},
                    {min: 11, max: 11, message: '长度应为 11 个数字', trigger: 'blur'}
                ]
            }
        }
    },
    methods: {
        check_form: function (task) {
            this.$refs["form"].validate((valid) => {
                if (valid) {
                    console.log("Check success, submit!");
                    if (task === "get_task") {
                        this.user_task();
                    } else if (task === "del_task") {
                        this.user_logout();
                    }
                }
            });
        },
        user_task: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/user/task`,
                {
                    params: {
                        username: this.formData.username,
                        phone: this.formData.phone,
                    }
                })
                .then(function (res) {
                    that.loading = false
                    if (res.data.status === "success") {
                        that.taskInfo = res.data.data
                    }
                })
        },
        user_logout: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                phone: this.formData.phone,
            }
            this.$http.post(data_host + `/user/logout`, http_data)
                .then(function (res) {
                    console.log(res)
                    that.loading = false;
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'success'
                        });
                        that.$router.push("/list");
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                })
        }
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

    .info {
        margin-top: 36px;

        .item {
            margin-bottom: 12px;

            p {
                margin: 0.5em 0;
            }

            .key {
                border-radius: 4px;
                background-color: rgba(145, 190, 240, 0.3);
            }

            .val {
                background-color: rgba(145, 190, 240, 0.1);
            }
        }

    }

    .form {
        width: 90%;
        margin-top: 36px;
        display: inline-block;
        text-align: center;
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
<template>
    <div class="wb-home">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>输入信息门户账号即可添加自动签到任务</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <div class="alert">
                <el-alert :title="closeInfo" type="error" center
                          v-if="closeLogin" :closable="false"></el-alert>
            </div>
            <el-form class="form" ref="form" label-position="left" label-width="60px"
                     v-loading="loading" :rules="rules" :model="formData">
                <el-form-item label="账号" prop="username">
                    <el-input v-model="formData.username" placeholder="信息门户账户" :disabled="closeLogin"></el-input>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="formData.password" placeholder="不会存储密码"
                              show-password :disabled="closeLogin"></el-input>
                </el-form-item>
                <el-form-item label="昵称" prop="nickname">
                    <el-input v-model="formData.nickname" placeholder="起个帅气名字" :disabled="closeLogin"></el-input>
                </el-form-item>
                <el-form-item label="手机" prop="phone">
                    <el-input v-model="formData.phone" placeholder="用于身份认证" type="number"
                              :disabled="closeLogin"></el-input>
                </el-form-item>
                <el-button type="success" @click="check_form" plain :disabled="closeLogin">提交任务</el-button>
            </el-form>
            <div class="tips">
                <h2>这是什么？</h2>
                <p>都啥时候了<br/>
                    你还在手动打卡吗？<br/>
                    为了给懒中懒的你一个放松的机会<br/>
                    自动打卡脚本改写为在线的自动签到服务了<br/>
                    仅需要账号密码登录一次后<br/>
                    即可为你每天自动打卡<br/>
                    再也不用惦记了<br/>
                </p>
                <h2>要怎么用？</h2>
                <p>只要你打过卡<br/>
                    服务程序会定时重打卡<br/>
                    使用的是上一次的打卡数据(包括位置)<br/>
                    如果要修改你的打卡信息<br/>
                    在任务设定的时间前<br/>
                    自己打卡就好<br/>
                </p>
                <h2>这安全吗？</h2>
                <p>不存储你的密码<br/>
                    服务使用SSL加密传输<br/>
                    仅在登录时使用账号密码<br/>
                    登录后打卡网站提供的Cookie<br/>
                    之后每一天都使用Cookie进行签到<br/>
                    Cookie无法用于获取其他信息<br/>
                    而且源码是开源的<br/>
                    接受安全反馈<br/>
                    <a href="https://github.com/wolfbolin/CSU-COVID19-SIGN" target="_blank">Github</a><br/>
                </p>
                <h2>为什么要手机？</h2>
                <p>在删除时进行校验<br/>
                    在账号出现问题时短信联系<br/>
                    向VIP用户推送每日的打开结果<br/>
                    若需要VIP短信推送服务<br/>
                    请联系开发者开通
                </p>
                <h2>会宕机吗？</h2>
                <p>理论上会<br/>
                    但是还没发生过<br/>
                    自动打卡脚本已经很久了<br/>
                    一直能稳定运行<br/>
                    用就完事了
                </p>
                <h2>以防万一</h2>
                <p>由于使用量增加<br/>
                    防止突如其来的服务中断<br/>
                    给你本来懒惰的打卡生活增添困扰<br/>
                    所以我建议你加入服务反馈群1158608406<br/>
                    如果出现奇奇怪怪的问题导致服务中断<br/>
                    会尽快通知各位自行打卡<br/>
                    @全体成员
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Home',
    data() {
        return {
            loading: false,
            closeInfo: "",
            closeLogin: false,
            formData: {
                username: "",
                password: "",
                nickname: "",
                phone: ""
            },
            rules: {
                username: [
                    {required: true, message: '请输入信息门户账户', trigger: 'blur'},
                    {min: 6, max: 14, message: '长度在 6 到 14 个字符', trigger: 'blur'}
                ],
                password: [
                    {required: true, message: '请输入信息门户密码', trigger: 'blur'}
                ],
                nickname: [
                    {required: true, message: '给自己起个名字吧', trigger: 'blur'},
                    {min: 4, max: 16, message: '长度在 4 到 16 个字符', trigger: 'blur'}
                ],
                phone: [
                    {required: true, message: '请输入收信电话号码', trigger: 'blur'},
                    {min: 11, max: 11, message: '长度应为 11 个数字', trigger: 'blur'}
                ]
            }
        }
    },
    methods: {
        check_open: function(){
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host
            this.$http.get(data_host + `/user/open`)
                .then(function (res) {
                    console.log(res)
                    that.loading = false;
                    if (res.data.status !== 'success') {
                        that.closeLogin = true
                        that.closeInfo = res.data.message
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                })
        },
        check_form: function () {
            this.$refs["form"].validate((valid) => {
                if (valid) {
                    console.log("Check success, submit!");
                    this.user_login();
                } else {
                    console.log('"Check error"');
                    return false;
                }
            });
        },
        user_login: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                password: this.formData.password,
                nickname: this.formData.nickname,
                phone: this.formData.phone
            }
            console.log(http_data)
            this.$http.post(data_host + `/user/login`, http_data)
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
    },
    mounted() {
        this.check_open()
    }
}
</script>

<style lang="scss" scoped>
.wb-home {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
    }

    .alert {
        width: 60%;
        margin: 12px auto;
    }

    .form {
        width: 90%;
        margin-top: 36px;
        display: inline-block;
        text-align: center;
    }

    .el-date-editor.el-input {
        width: 100%;
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

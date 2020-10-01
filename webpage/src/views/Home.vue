<template>
    <div class="wb-home">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>键入信息门户账号以及其他基本信息<br/>添加每日自动签到任务</p>
            <el-form class="form" ref="form" label-position="left" label-width="60px"
                     v-loading="loading" :rules="rules" :model="formData">
                <el-form-item label="账号" prop="username">
                    <el-input v-model="formData.username" placeholder="信息门户账户"></el-input>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="formData.password" placeholder="不会存储密码" show-password></el-input>
                </el-form-item>
                <el-form-item label="昵称" prop="nickname">
                    <el-input v-model="formData.nickname" placeholder="起个帅气名字"></el-input>
                </el-form-item>
                <el-form-item label="手机" prop="phone">
                    <el-input v-model="formData.phone" placeholder="用于发送结果" type="number"></el-input>
                </el-form-item>
                <el-form-item label="时间" prop="time">
                    <el-time-picker v-model="formData.time" :picker-options="{selectableRange: '00:01:00 - 10:00:00'}"
                                    format="HH:mm" value-format="HH:mm" placeholder="选择打卡时间">
                    </el-time-picker>
                </el-form-item>
                <el-button type="success" @click="check_form" plain>提交任务</el-button>
            </el-form>
            <div class="tips">
                <h2>这是什么？</h2>
                <p>都十月份了<br/>
                    你还在手动打卡吗？<br/>
                    为了给懒中懒得你一个放松的机会<br/>
                    自动打卡脚本改写为在线的自动签到服务了<br/>
                    仅需要账号密码登录一次后<br/>
                    即可为你每天自动打卡
                </p>
                <h2>要怎么用？</h2>
                <p>只要你打过卡<br/>
                    每日程序会定时重打开<br/>
                    用的是你前一日的打卡数据<br/>
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
            formData: {
                username: "",
                password: "",
                nickname: "",
                phone: "",
                time: ""
            },
            rules: {
                username: [
                    {required: true, message: '请输入信息门户账户', trigger: 'blur'},
                    {min: 8, max: 14, message: '长度在 8 到 14 个字符', trigger: 'blur'}
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
                ],
                time: [
                    {required: true, message: '请选择打卡时间', trigger: 'change'}
                ],
            }
        }
    },
    methods: {
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
                phone: this.formData.phone,
                time: this.formData.time,
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
                    }else{
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
}
</script>

<style lang="scss" scoped>
.wb-home {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
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

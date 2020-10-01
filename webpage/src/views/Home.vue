<template>
    <div class="wb-home">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>键入信息门户账号以及其他基本信息<br/>开启每日自动签到</p>
            <el-form class="form" ref="form" label-position="left" label-width="60px"
                     v-loading="loading" :rules="rules" :model="formData">
                <el-form-item label="账号" prop="username">
                    <el-input v-model="formData.username" placeholder="信息门户账户" type="number"></el-input>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="formData.password" placeholder="不会存储密码" show-password></el-input>
                </el-form-item>
                <el-form-item label="昵称" prop="nickname">
                    <el-input v-model="formData.nickname" placeholder="给自己起名字"></el-input>
                </el-form-item>
                <el-form-item label="手机" prop="phone">
                    <el-input v-model="formData.phone" placeholder="用于发送结果" type="number"></el-input>
                </el-form-item>
                <el-form-item label="时间" prop="time">
                    <el-time-picker v-model="formData.time" :picker-options="{selectableRange: '00:01:00 - 10:00:00'}"
                                    format="HH:mm" value-format="HH:mm" placeholder="选择打卡时间">
                    </el-time-picker>
                </el-form-item>
                <el-button type="success" @click="check_form" plain>提交验证</el-button>
            </el-form>
            <div class="tips">
                <h2>阿巴阿巴</h2>
                <p>阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴阿巴</p>
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
    }
}

</style>

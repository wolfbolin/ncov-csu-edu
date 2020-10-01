<template>
    <div class="wb-unbind">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>键入关键检验信息以取消自动签到服务</p>
            <el-form class="form" ref="form" label-position="left" label-width="60px"
                     v-loading="loading" :rules="rules" :model="formData">
                <el-form-item label="账号" prop="username">
                    <el-input v-model="formData.username" placeholder="信息门户账户"></el-input>
                </el-form-item>
                <el-form-item label="手机" prop="phone">
                    <el-input v-model="formData.phone" placeholder="用于发送结果" show-password></el-input>
                </el-form-item>
                <el-button type="success" @click="check_form" plain>删除任务</el-button>
            </el-form>
            <div class="tips">
                <h2>有啥问题</h2>
                <p>认真的？<br/>
                    这么实在的工具为何放弃？<br/>
                    信息填错重写登录即可覆盖现在的<br/>
                    删除功能做着玩的(能用)<br/>
                    你为啥要用<br/>
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "Unbind",
    data() {
        return {
            loading: false,
            formData: {
                username: "",
                phone: ""
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
                phone: this.formData.phone,
            }
            console.log(http_data)
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
.wb-unbind {
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
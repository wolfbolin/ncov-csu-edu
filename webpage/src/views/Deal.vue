<template>
    <div class="wb-unbind">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>让我们一起建立更加深刻的契约吧</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <div class="wb-order">
                <el-row :gutter="20" class="wb-alipay">
                    <el-col :xs="24" :sm="16">
                        <el-form :model="order" :rules="payRule" ref="payForm"
                                 label-width="80px" label-position="right"
                                 class="wb-alipay-form">
                            <el-form-item label="选择功能" style="text-align: left" prop="itemList">
                                <el-checkbox-group v-model="order.itemList" size="small" @change="choose_change">
                                    <template v-for="item in menu">
                                        <el-checkbox v-bind:key="item.name" :label="item.name"
                                                     class="wb-checkbox" border></el-checkbox>
                                    </template>
                                </el-checkbox-group>
                            </el-form-item>
                            <el-form-item label="捐助金额" prop="donation"
                                          v-if="order.itemList.indexOf('友情捐助') !== -1">
                                <el-slider v-model="order.donation" :min="1" :max="200"
                                           @change="choose_change" style="padding: 0 12px"></el-slider>
                            </el-form-item>
                            <el-form-item label="用户学号" prop="username">
                                <el-input type="text" v-model="order.username"></el-input>
                            </el-form-item>
                            <el-form-item label="手机号码" prop="phone">
                                <el-input type="text" v-model="order.phone"></el-input>
                            </el-form-item>
                            <el-form-item label="支付留言" prop="attach">
                                <el-input type="textarea" v-model="order.attach" maxlength="128"
                                          show-word-limit></el-input>
                            </el-form-item>
                            <el-button @click="query_payment" v-if="order.order_status !== '未创建'">
                                刷新
                            </el-button>
                            <el-button type="primary" @click="precreat_payment" v-else>
                                提交
                            </el-button>
                        </el-form>
                    </el-col>
                    <el-col :xs="24" :sm="8" class="wb-alipay-qrcode">
                        <p>交易金额：{{ order.volume }}元(RMB)</p>
                        <img v-if="order.order_status === '未创建'"
                             src="@/assets/QR_Code.png" alt="qrcode"/>
                        <img v-else-if="order.order_status === '已支付'"
                             src="@/assets/done.png" alt="qrcode"/>
                        <div v-else>
                            <vue-qr :text="order.order_link"></vue-qr>
                            <el-button type="primary" @click="open_app" plain>打开手机应用支付</el-button>
                        </div>
                        <p>状态：{{ order.order_status }}</p>
                        <p>订单号：{{ order.order_str }}</p>
                    </el-col>
                </el-row>
            </div>
            <div class="readme">
                <h2>荣誉贡献者</h2>
                <div>
                    <template v-for="donor in donor_list">
                        <el-tag :key="donor">{{ donor }}</el-tag>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import vueQr from 'vue-qr'

export default {
    components: {vueQr},
    name: "Unbind",
    data() {
        let checkPhone = (rule, value, callback) => {
            if (!value) {
                return callback(new Error('请输入登录手机号'));
            } else {
                const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
                if (reg.test(value)) {
                    return callback();
                } else {
                    return callback(new Error('请输入登录手机号'));
                }
            }
        };
        return {
            timer: null,
            itemList: [],
            qrcode_image: "",
            order: {
                itemList: [],
                donation: 0,
                volume: 0,
                username: "",
                phone: "",
                attach: "",
                order_str: "Bill-xxxxxxxxx",
                order_link: "",
                order_status: "未创建",
            },
            menu: [],
            payRule: {
                itemList: [
                    {required: true, message: "至少选择一个吧", trigger: "change"}
                ],
                subject: [
                    {required: true, message: "请输入商品名称", trigger: "blur"},
                    {min: 3, max: 15, message: "3-15个字符哦", trigger: "blur"},
                ],
                donation: [
                    {required: true, message: "请输入捐助金额", trigger: "blur"},
                    {type: 'number', message: "这个数目不合适", min: 1, max: 200, trigger: "blur"}
                ],
                phone: [
                    {required: true, message: "请输入登录手机号", trigger: "blur"},
                    {validator: checkPhone, trigger: "blur"}
                ],
                username: [
                    {required: true, message: "请输入登录用户学号", trigger: "blur"},
                    {min: 6, max: 14, message: "请输入登录用户学号", trigger: "blur"},
                ],
                attach: [
                    {min: 0, max: 128, message: "太长了，太长了", trigger: "blur"},
                ]
            },
            donor_list: []
        }
    },
    methods: {
        open_app: function () {
            window.open(this.order.order_link)
        },
        choose_change: function () {
            let volume = 0
            for (let choose of this.order.itemList) {
                for (let item of this.menu) {
                    if (item.name === choose) {
                        volume += item.volume
                        break
                    }
                }
            }
            if (this.order.itemList.indexOf('友情捐助') !== -1) {
                this.order.volume = volume + this.order.donation
            }
        },
        fetch_volume: function () {
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/deal/menu`
            this.$http.get(http_url)
                .then(function (res) {
                    console.log(res.data)
                    if (res.data.status === "success") {
                        that.menu = res.data.data
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        },
        fetch_donor: function () {
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/user/donor`
            this.$http.get(http_url)
                .then(function (res) {
                    console.log(res.data)
                    if (res.data.status === "success") {
                        that.donor_list = res.data.data
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        },
        precreat_payment: function () {
            this.$refs["payForm"].validate((valid) => {
                    if (valid) {
                        console.log("Creat deal order")
                        // 数据预处理
                        let itemList = []
                        for (let choose of this.order.itemList) {
                            for (let item of this.menu) {
                                if (item.name === choose) {
                                    itemList.push(item.key)
                                    break
                                }
                            }
                        }

                        // 创建交易订单
                        let that = this;
                        let data_host = this.$store.state.host;
                        let http_url = data_host + `/deal/order`
                        this.$http.post(http_url,
                            {
                                username: this.order.username,
                                phone: this.order.phone,
                                donation: this.order.donation,
                                attach: this.order.attach,
                                item_list: itemList,
                            })
                            .then(function (res) {
                                if (res.data.status === "success") {
                                    let order_info = res.data.data
                                    that.order.order_status = "已创建"
                                    that.order.order_str = order_info["order_str"]
                                    that.order.order_link = order_info["qrcode_link"]
                                    that.timer = setInterval(that.query_payment, 2000)
                                } else {
                                    that.$message({
                                        message: res.data.message,
                                        type: 'error'
                                    });
                                }
                            })
                            .catch(function (res) {
                                console.log(res)
                            })
                    }
                }
            )
        },
        query_payment: function () {
            console.log("Check deal order")
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/deal/order`
            this.$http.get(http_url, {
                params: {
                    phone: this.order.phone,
                    username: this.order.username,
                    order_str: this.order.order_str,
                }
            })
                .then(function (res) {
                    if (res.data.status === "success") {
                        console.log(res.data)
                        switch (res.data.order_status) {
                            case "NOT_EXIST":
                                that.order.order_status = "未创建";
                                break;
                            case "CREATE":
                                that.order.order_status = "已创建";
                                break;
                            case "WAITING":
                                that.order.order_status = "待支付";
                                break;
                            case "SUCCESS":
                                that.order.order_status = "已支付";
                                break;
                            case "FINISH":
                                that.order.order_status = "已终止";
                                break;
                            case "CLOSE":
                                that.order.order_status = "已关闭";
                                break;
                            default:
                                that.order.order_status = "未知";
                        }
                        if (["已支付", "已终止", "已关闭"].indexOf(that.order.order_status) !== -1) {
                            clearInterval(that.timer)
                        }
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        }
    },
    mounted() {
        this.fetch_volume()
        this.fetch_donor()
    }
}
</script>

<style lang="scss" scoped>
.wb-unbind {
    .wb-order {
        width: 70%;
        margin-top: 32px;
        display: inline-block;

        .wb-checkbox {
            margin-right: 10px;
        }

        .wb-alipay-form {
            .el-button {
                width: 60%;
                margin-bottom: 36px;
            }
        }
    }

    .el-tag {
        height: 48px;
        padding: 0 20px;
        line-height: 48px;
        font-size: 16px;
        margin: 10px;
    }
}
</style>
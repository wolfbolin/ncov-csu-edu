<template>
    <div class="wb-about">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>关于该服务的其他事情</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <div class="tips">
                <h2>开发者</h2>
                <p>WolfBolin<br/>
                    可以选择以下方式联系我<br/>
                    我的主页：<a href="https://wolfbolin.com" target="_blank">https://wolfbolin.com</a><br/>
                    我的博客：<a href="https://blog.wolfbolin.com" target="_blank">https://blog.wolfbolin.com</a><br/>
                    我的E-Mail：<a href="mailto:mailto@wolfbolin.com" target="_blank">mailto@wolfbolin.com</a><br/>
                    我的Github：<a href="https://github.com/wolfbolin" target="_blank">WolfBolin Github</a><br/>
                    我的BiliBili：<a href="https://space.bilibili.com/72835041" target="_blank">WolfBolin BiliBili</a>
                </p>
                <h2>项目贡献者</h2>
                <p><a href="https://github.com/kongmoumou" target="_blank">kongmoumou Github</a><br/>
                </p>
                <h2>未完待续</h2>
                <p>最后更新时间<br/>
                    2020-11-11
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'List',
    data() {
        return {}
    },
    methods: {},
    mounted() {}
}
</script>

<style lang="scss" scoped>
.wb-about {
    .userChart {
        width: 100%;
        margin-top: 16px;
    }

    .signChart {
        width: 100%;
        margin-top: 16px;
    }
}
</style>

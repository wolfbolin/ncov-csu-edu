<template>
    <div class="wb-about">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>关于该服务的其他事情</p>
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
                    2020-10-06 18:55
                </p>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.wb-about {
    text-align: center;

    .logo {
        margin: 128px 0 64px 0;
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

import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        host: "",
        group: "839482549"
    },
    mutations: {
        setData(state, param) {
            let val = param.val;
            if (typeof param.val == "object") {
                val = JSON.stringify(val);
            } else if (typeof param.val == "string") {
                val = `"${val}"`
            }
            eval(`state.${param.key}=${val}`);
        }
    },
    actions: {},
    modules: {}
})

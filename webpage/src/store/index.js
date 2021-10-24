import Vue from 'vue'
import Vuex from 'vuex'
import Host from './host_config.json'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        host: "",
        host_config: Host,
        group: "205161441"
    },
    mutations: {
        setData(state, param) {
            let val = param.val;
            if (typeof param.val == "object") {
                val = JSON.stringify(val);
            } else if (typeof param.val == "string") {
                val = `"${val}"`
            }
            eval(`state.${param.key} = ${val}`);
        }
    },
    actions: {},
    modules: {}
})

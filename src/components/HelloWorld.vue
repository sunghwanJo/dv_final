<template>
    <v-app>
        <v-content>
            <v-container>
                <v-layout v-if="user == null" wrap :class="['text-xs-center', 'mb-4']">
                    <v-flex xs12>
                        <div :class="'display-1'">Instagram 유사인물 찾기</div>

                        <v-text-field
                                v-model="tag"
                                name="input-1"
                                label="사용자의 태그를 입력하세요"
                        >taeri__taeri
                        </v-text-field>
                        <v-btn
                                @click.prevent="getUser"
                                :loading="loading"
                                outline
                                color="indigo">확인
                        </v-btn>
                    </v-flex>
                </v-layout>

                <v-layout v-if="user != null" wrap :class="['text-xs-center', 'mt-3']">
                    <v-flex xs4>
                        <v-card :class="'pa-4'">
                            <v-card-media :src="user.profile_image" height="200px">
                            </v-card-media>
                            <div class="title">{{user.tag}}</div>
                            <bar-chart :chart-data="user_chart"></bar-chart>
                        </v-card>
                    </v-flex>
                    <v-flex xs4 :class="'indigo--text'">
                        <div :class="['display-1', 'mb-4']"></div>
                        <span :class="['display-4']">{{ tsi_ratio }}</span>
                        <span class="display-1">%</span>
                        <div class="title">일치합니다</div>
                    </v-flex>
                    <v-flex xs4>
                        <v-card :class="'pa-4'">
                            <v-card-media :src="similar_user.profile_image" height="200px">
                            </v-card-media>
                            <div class="title">{{similar_user.tag}}</div>
                            <bar-chart :chart-data="f_user_chart"></bar-chart>
                        </v-card>
                    </v-flex>
                </v-layout>
            </v-container>
        </v-content>
    </v-app>
</template>

<script type="text/ecmascript-6">
    import axios from 'axios'
    import BarChart from '../components/BarChart.vue'

    export default {
        components: {
            BarChart,
        },
        data () {
            return {
                tag: null,
                loading: false,
                user: null,
                similar_user: {},
                tsi_ratio: 0,

                user_chart: null,
                f_user_chart: null
            }
        },
        methods: {
            getUser(tag){
                this.loading = true
                axios.get('/taeri__taeri/results/')
                        .then(response => {
                            this.user = response.data.user;
                            this.similar_user = response.data.similar_user;
                            this.user_chart = {
                                labels: this.user.word_label,
                                datasets: [
                                    {
                                        label: '빈도수',
                                        backgroundColor: '#3f51b5',
                                        data: this.user.word_data
                                    }
                                ]
                            };

                            this.f_user_chart = {
                                labels: this.similar_user.word_label,
                                datasets: [
                                    {
                                        label: '빈도수',
                                        backgroundColor: '#3f51b5',
                                        data: this.similar_user.word_data
                                    }
                                ]
                            }

                            this.tsi_ratio = parseInt((response.data.tsi_ratio) * 100);
                            this.loading = false
                        })
                        .catch(e => {
                            console.log(e)
                            this.loading = false
                        })
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    h1, h2 {
        font-weight: normal;
    }

    ul {
        list-style-type: none;
        padding: 0;
    }

    li {
        display: inline-block;
        margin: 0 10px;
    }

    a {
        color: #42b983;
    }
</style>

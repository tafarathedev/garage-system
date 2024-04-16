odoo.define('car_repair_maintenance_axis.MyCustomActionNew',  function (require) {
"use strict";
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
//var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var MyCustomActionNew = AbstractAction.extend({
    template: 'CarDashboardView',

    jsLibs: [
        '/car_repair_maintenance_axis/static/src/js/Chart.js',

    ],
    events: {
        'click .action-received': 'action_received',
        'click .action-in-diagnosis': 'action_in_diagnosis',
        'click .action-in-progress': 'action_in_progress',
        'click .action-done': 'action_done',
        'click .action-in-checklist': 'action_in_checklist',
        'click .action-in-equipment': 'action_in_equipment',
        'click .action-team': 'action_in_team',
        },


    init: function(parent, context) {
        this._super(parent, context);
        var self = this;
    },

    start: function() {
        var self = this;
        self.render_dashboards();
        self.render_graphs();
        return this._super();
    },

    reload: function () {
            window.location.href = this.href;
    },

    render_dashboards: function(value) {
        var self = this;
        var car_repair_dashboard = QWeb.render('CarDashboardView', {
            widget: self,
        });

        rpc.query({
                model: 'car.repair.form',
                method: 'get_car_repair_count_list',
                args: []
            })
            .then(function (result){
            self.$el.find('.state-received').text(result['received_count'])
            self.$el.find('.state-in-diagnosis').text(result['in_diagnosis_count'])
            self.$el.find('.state-in-progress').text(result['in_progress_count'])
            self.$el.find('.state-done').text(result['done_count'])
            });

        return car_repair_dashboard
    },

    action_in_checklist:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Service Repair CheckList"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.checklist',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)
    },

    action_in_team:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Job Roles"),
            type: 'ir.actions.act_window',
            res_model: 'job.roles',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)
    },

    action_in_equipment:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Car Parts"),
            type: 'ir.actions.act_window',
            res_model: 'car.parts',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)


    },

     action_received:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Cars Received"),
            type: 'ir.actions.act_window',
            res_model: 'car.repair.form',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','received']],
            target: 'current'
        },)
    },

    action_in_diagnosis:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Cars In Diagnosis"),
            type: 'ir.actions.act_window',
            res_model: 'car.repair.form',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','diagnosis']],
            target: 'current'
        },)
    },

    action_in_progress:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Cars In-Progress"),
            type: 'ir.actions.act_window',
            res_model: 'car.repair.form',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','progress']],
            target: 'current'
        },)
    },

    action_done:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Cars Done"),
            type: 'ir.actions.act_window',
            res_model: 'car.repair.form',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','done']],
            target: 'current'
        },)
    },


    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    render_graphs: function(){
        var self = this;
        self.graph_car_repair_weekly_data();
        self.graph_monthly_car_repair_data()
    },

     graph_car_repair_weekly_data: function() {
        var self = this;
        var ctx = this.$el.find('#highprice')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'car.repair.form',
                method: 'get_car_repair_week_data',
            })
            .then(function (result) {
                var data = result.data;
                var day = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
                var week_data = [];
                if (data){
                    for(var i = 0; i < day.length; i++){
                        day[i] == data[day[i]]
                        var day_data = day[i];
                        var day_count = data[day[i]];
                        if(!day_count){
                                day_count = 0;
                        }
                        week_data[i] = day_count

                    }
                }

                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {

                    labels: day ,
                    datasets: [{
                        label: 'Cars In Diagnosis',
                        data: week_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 5,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 2,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,week_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                },
            },
        });
            });
    },

     graph_monthly_car_repair_data: function() {
     var self = this;
        var ctx = this.$el.find('#monthlymaintenance')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'car.repair.form',
                method: 'get_car_repair_statistics_data',
            })
            .then(function (result) {
                var data = result.data
                var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                'August', 'September', 'October', 'November', 'December']
                var month_data = [];

                if (data){
                    for(var i = 0; i < months.length; i++){
                        months[i] == data[months[i]]
                        var day_data = months[i];
                        var month_count = data[months[i]];
                        if(!month_count){
                                month_count = 0;
                        }
                        month_data[i] = month_count

                    }
                }
                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {

                    labels: months,
                    datasets: [{
                        label: ' Car Repaired',
                        data: month_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 1,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 1,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,month_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                },
            },
        });

            });


    },

});


core.action_registry.add("car_repair_dashboard", MyCustomActionNew);
return MyCustomActionNew
});

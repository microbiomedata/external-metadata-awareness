<div align="center">
    <h2>Frappe Gantt Custom Mod</h2>
    <p align="center">
        <p>This Gantt chart app is used as the backbone of the <a href="https://github.com/cancerDHC/dashboard">
        CCDH GitHub ticket visualization dashboard</a>.</p>
        <p>It is a customization of the original <a href="https://github.com/frappe/gantt">Frappe Gant</a> project
        <br />with improvements from 
        <a href="https://github.com/Alisher778/frappe-gantt-extended/tree/dragging">Alisher778</a>,
        <a href="https://github.com/jamieday/gantt/tree/task_groups">jaimeday</a>, 
        <a href="https://github.com/fredybawa/gantt/commit/8b94aa97fdec373ac09d0ae6912e948f8fe9d0a1">fredybawa</a>,
         and Jen Martin.
    </p>
</div>

<p align="center">
    <img src="https://cloud.githubusercontent.com/assets/9355208/21537921/4a38b194-cdbd-11e6-8110-e0da19678a6d.png">
</p>



### Usage
Include the compiled JS and CSS files in the main HTML page:
```
<script src="frappe-gantt.min.js"></script>
<link rel="stylesheet" href="frappe-gantt.css">
```

The Gantt chart is a collection of tasks with the following format. To create a chart, get/create the tasks and then call the Gantt constructor:
```js
var tasks = [
  {
    id: 'Task 1',
    group_id: 'design',
    name: 'Redesign website',
    start: '2016-12-28',
    end: '2016-12-31',
    progress: 20,
    dependencies: 'Task 2, Task 3',
    custom_class: 'bar-milestone' // optional
  },
  ...
]
var gantt = new Gantt("#gantt", tasks);
```

You can also pass various options to the Gantt constructor:
```js
var gantt = new Gantt("#gantt", tasks, {
    header_height: 50,
    column_width: 30,
    step: 24,
    view_modes: ['Quarter Day', 'Half Day', 'Day', 'Week', 'Month'],
    bar_height: 20,
    bar_corner_radius: 3,
    arrow_curve: 5,
    padding: 18,
    view_mode: 'Day',
    date_format: 'YYYY-MM-DD',
    custom_popup_html: null,
    draggable: true,
    hasArrows: true,
    groups: [ 
        {
            'id': 'design', 
            'name': 'Web Design',
            'bar_class': 'bar-design-group'
        }
    ]
});
```

### To Continue Development

1. Clone this repo.
2. `cd` into project directory
3. `yarn`
4. `yarn run dev`

Install using the command:
```
npm install frappe-gantt
```

### Original Frappe Gantt Project Information

License: MIT

Project maintained by [frappe](https://github.com/frappe)

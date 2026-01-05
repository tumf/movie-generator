// pb_migrations/1687801090_create_jobs.js

migrate((app) => {
    // Check if jobs collection already exists
    try {
        let existing = app.findCollectionByNameOrId("jobs")
        if (existing) {
            console.log("Jobs collection already exists, skipping")
            return
        }
    } catch (e) {
        // Collection doesn't exist, create it
    }

    let collection = new Collection({
        type: "base",
        name: "jobs",
        listRule: "",
        viewRule: "",
        createRule: "",
        updateRule: "",
        deleteRule: "",
        fields: [
            {
                type: "text",
                name: "url",
                required: true,
                max: 2048,
            },
            {
                type: "text",
                name: "status",
                required: true,
                max: 50,
            },
            {
                type: "number",
                name: "progress",
                required: false,
                min: 0,
                max: 100,
            },
            {
                type: "text",
                name: "progress_message",
                required: false,
                max: 500,
            },
            {
                type: "text",
                name: "current_step",
                required: false,
                max: 100,
            },
            {
                type: "text",
                name: "client_ip",
                required: true,
                max: 50,
            },
            {
                type: "text",
                name: "video_path",
                required: false,
                max: 500,
            },
            {
                type: "number",
                name: "video_size",
                required: false,
            },
            {
                type: "text",
                name: "error_message",
                required: false,
                max: 2000,
            },
            {
                type: "date",
                name: "started_at",
                required: false,
            },
            {
                type: "date",
                name: "completed_at",
                required: false,
            },
            {
                type: "date",
                name: "expires_at",
                required: true,
            },
            {
                type: "autodate",
                name: "created",
                onCreate: true,
                onUpdate: false,
            },
            {
                type: "autodate",
                name: "updated",
                onCreate: true,
                onUpdate: true,
            },
        ],
    })

    app.save(collection)
}, (app) => {
    try {
        let collection = app.findCollectionByNameOrId("jobs")
        app.delete(collection)
    } catch {
        // silent errors (probably already deleted)
    }
})

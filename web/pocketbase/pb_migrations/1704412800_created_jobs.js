/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "jobs",
    "name": "jobs",
    "type": "base",
    "system": false,
    "schema": [
      {
        "id": "url",
        "name": "url",
        "type": "text",
        "required": true,
        "presentable": false,
        "options": {
          "min": null,
          "max": 2048,
          "pattern": ""
        }
      },
      {
        "id": "status",
        "name": "status",
        "type": "select",
        "required": true,
        "presentable": false,
        "options": {
          "maxSelect": 1,
          "values": [
            "pending",
            "processing",
            "completed",
            "failed",
            "cancelled"
          ]
        }
      },
      {
        "id": "progress",
        "name": "progress",
        "type": "number",
        "required": true,
        "presentable": false,
        "options": {
          "min": 0,
          "max": 100,
          "noDecimal": true
        }
      },
      {
        "id": "progress_message",
        "name": "progress_message",
        "type": "text",
        "required": false,
        "presentable": false,
        "options": {
          "min": null,
          "max": 500,
          "pattern": ""
        }
      },
      {
        "id": "current_step",
        "name": "current_step",
        "type": "text",
        "required": false,
        "presentable": false,
        "options": {
          "min": null,
          "max": 100,
          "pattern": ""
        }
      },
      {
        "id": "video_path",
        "name": "video_path",
        "type": "text",
        "required": false,
        "presentable": false,
        "options": {
          "min": null,
          "max": 1024,
          "pattern": ""
        }
      },
      {
        "id": "video_size",
        "name": "video_size",
        "type": "number",
        "required": false,
        "presentable": false,
        "options": {
          "min": null,
          "max": null,
          "noDecimal": true
        }
      },
      {
        "id": "error_message",
        "name": "error_message",
        "type": "text",
        "required": false,
        "presentable": false,
        "options": {
          "min": null,
          "max": 2048,
          "pattern": ""
        }
      },
      {
        "id": "client_ip",
        "name": "client_ip",
        "type": "text",
        "required": true,
        "presentable": false,
        "options": {
          "min": null,
          "max": 45,
          "pattern": ""
        }
      },
      {
        "id": "started_at",
        "name": "started_at",
        "type": "date",
        "required": false,
        "presentable": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "id": "completed_at",
        "name": "completed_at",
        "type": "date",
        "required": false,
        "presentable": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "id": "expires_at",
        "name": "expires_at",
        "type": "date",
        "required": true,
        "presentable": false,
        "options": {
          "min": "",
          "max": ""
        }
      }
    ],
    "indexes": [
      "CREATE INDEX idx_jobs_status ON jobs (status)",
      "CREATE INDEX idx_jobs_client_ip ON jobs (client_ip)",
      "CREATE INDEX idx_jobs_expires_at ON jobs (expires_at)",
      "CREATE INDEX idx_jobs_created ON jobs (created)"
    ],
    "listRule": null,
    "viewRule": null,
    "createRule": null,
    "updateRule": null,
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("jobs");

  return dao.deleteCollection(collection);
});

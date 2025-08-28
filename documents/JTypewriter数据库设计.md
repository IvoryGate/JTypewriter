# JTypewriter数据库设计

sqlite

## 表设计结构

### 数据库表目录

| **序号** |   **表名**   | **注释/说明** |
| :------: | :----------: | :-----------: |
|    0     |    users     |    用户表     |
|    1     |   sessions   |  练习数据表   |
|    2     | Achievements |     成就      |
|    3     |   settings   |   应用设置    |

### 数据库表结构

#### users

|  **字段**  | **类型** | **是否为空** |   **注释**   |
| :--------: | :------: | :----------: | :----------: |
|     id     | INTEGER  |      NO      | 主键（自增） |
|  username  |   TEXT   |      NO      |    用户名    |
| created_at | DATETIME |      NO      |   创建时间   |
|   level    |   TEXT   |      NO      |   用户水平   |
|            |          |              |              |


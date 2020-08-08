CREATE TABLE `users` (
    `id` INT(8) unsigned NOT NULL AUTO_INCREMENT,
    `username` TEXT(255) NOT NULL,
    `password_hash` TEXT(255) NOT NULL,
    `salt` Text(8) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
);


CREATE TABLE `items` (
    `id` INT(8) unsigned NOT NULL AUTO_INCREMENT,
    `title` TEXT(255) NOT NULL,
    `body` TEXT(65535) NOT NULL,
    `user_id` INT(8) unsigned NOT NULL,
    `likes` TEXT(16383) DEFAULT NULL,
    `likes_count` INT(8) unsigned DEFAULT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
);

-- 後付けならこれでカラム追加してね
-- ALTER TABLE `items` ADD `likes_count` INT(8) unsigned DEFAULT NULL;

CREATE TABLE `icon` (
    `id` INT(8) unsigned NOT NULL AUTO_INCREMENT,
    `user_id` INT(8) unsigned NOT NULL,
    `icon` mediumblob NOT NULL,
    PRIMARY KEY (`id`)
);


CREATE TABLE `comments` (
    `id` INT(8) unsigned NOT NULL UNIQUE,
    `comment_001` JSON DEFAULT NULL,
    `comment_002` JSON DEFAULT NULL,
    `comment_003` JSON DEFAULT NULL,
    `comment_004` JSON DEFAULT NULL,
    `comment_005` JSON DEFAULT NULL,
    `comment_006` JSON DEFAULT NULL,
    `comment_007` JSON DEFAULT NULL,
    `comment_008` JSON DEFAULT NULL,
    `comment_009` JSON DEFAULT NULL,
    `comment_010` JSON DEFAULT NULL,
    `comment_011` JSON DEFAULT NULL,
    `comment_012` JSON DEFAULT NULL,
    `comment_013` JSON DEFAULT NULL,
    `comment_014` JSON DEFAULT NULL,
    `comment_015` JSON DEFAULT NULL,
    `comment_016` JSON DEFAULT NULL,
    `comment_017` JSON DEFAULT NULL,
    `comment_018` JSON DEFAULT NULL,
    `comment_019` JSON DEFAULT NULL,
    `comment_020` JSON DEFAULT NULL,
    `comment_021` JSON DEFAULT NULL,
    `comment_022` JSON DEFAULT NULL,
    `comment_023` JSON DEFAULT NULL,
    `comment_024` JSON DEFAULT NULL,
    `comment_025` JSON DEFAULT NULL,
    `comment_026` JSON DEFAULT NULL,
    `comment_027` JSON DEFAULT NULL,
    `comment_028` JSON DEFAULT NULL,
    `comment_029` JSON DEFAULT NULL,
    `comment_030` JSON DEFAULT NULL,
    `comment_031` JSON DEFAULT NULL,
    `comment_032` JSON DEFAULT NULL,
    `comment_033` JSON DEFAULT NULL,
    `comment_034` JSON DEFAULT NULL,
    `comment_035` JSON DEFAULT NULL,
    `comment_036` JSON DEFAULT NULL,
    `comment_037` JSON DEFAULT NULL,
    `comment_038` JSON DEFAULT NULL,
    `comment_039` JSON DEFAULT NULL,
    `comment_040` JSON DEFAULT NULL,
    `comment_041` JSON DEFAULT NULL,
    `comment_042` JSON DEFAULT NULL,
    `comment_043` JSON DEFAULT NULL,
    `comment_044` JSON DEFAULT NULL,
    `comment_045` JSON DEFAULT NULL,
    `comment_046` JSON DEFAULT NULL,
    `comment_047` JSON DEFAULT NULL,
    `comment_048` JSON DEFAULT NULL,
    `comment_049` JSON DEFAULT NULL,
    `comment_050` JSON DEFAULT NULL,
    `comment_051` JSON DEFAULT NULL,
    `comment_052` JSON DEFAULT NULL,
    `comment_053` JSON DEFAULT NULL,
    `comment_054` JSON DEFAULT NULL,
    `comment_055` JSON DEFAULT NULL,
    `comment_056` JSON DEFAULT NULL,
    `comment_057` JSON DEFAULT NULL,
    `comment_058` JSON DEFAULT NULL,
    `comment_059` JSON DEFAULT NULL,
    `comment_060` JSON DEFAULT NULL,
    `comment_061` JSON DEFAULT NULL,
    `comment_062` JSON DEFAULT NULL,
    `comment_063` JSON DEFAULT NULL,
    `comment_064` JSON DEFAULT NULL,
    `comment_065` JSON DEFAULT NULL,
    `comment_066` JSON DEFAULT NULL,
    `comment_067` JSON DEFAULT NULL,
    `comment_068` JSON DEFAULT NULL,
    `comment_069` JSON DEFAULT NULL,
    `comment_070` JSON DEFAULT NULL,
    `comment_071` JSON DEFAULT NULL,
    `comment_072` JSON DEFAULT NULL,
    `comment_073` JSON DEFAULT NULL,
    `comment_074` JSON DEFAULT NULL,
    `comment_075` JSON DEFAULT NULL,
    `comment_076` JSON DEFAULT NULL,
    `comment_077` JSON DEFAULT NULL,
    `comment_078` JSON DEFAULT NULL,
    `comment_079` JSON DEFAULT NULL,
    `comment_080` JSON DEFAULT NULL,
    `comment_081` JSON DEFAULT NULL,
    `comment_082` JSON DEFAULT NULL,
    `comment_083` JSON DEFAULT NULL,
    `comment_084` JSON DEFAULT NULL,
    `comment_085` JSON DEFAULT NULL,
    `comment_086` JSON DEFAULT NULL,
    `comment_087` JSON DEFAULT NULL,
    `comment_088` JSON DEFAULT NULL,
    `comment_089` JSON DEFAULT NULL,
    `comment_090` JSON DEFAULT NULL,
    `comment_091` JSON DEFAULT NULL,
    `comment_092` JSON DEFAULT NULL,
    `comment_093` JSON DEFAULT NULL,
    `comment_094` JSON DEFAULT NULL,
    `comment_095` JSON DEFAULT NULL,
    `comment_096` JSON DEFAULT NULL,
    `comment_097` JSON DEFAULT NULL,
    `comment_098` JSON DEFAULT NULL,
    `comment_099` JSON DEFAULT NULL,
    `comment_100` JSON DEFAULT NULL,
    PRIMARY KEY (`id`)
);

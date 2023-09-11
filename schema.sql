CREATE DATABASE IF NOT EXISTS `ss13_webmap`;
USE `ss13_webmap`;

-- Dumping structure for table ss13_webmap.codebases
CREATE TABLE IF NOT EXISTS `codebases` (
    `id` varchar(50) NOT NULL,
    `hash` varchar(50) NOT NULL,
    `last_checked` timestamp NULL DEFAULT NULL,
    `last_updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    `maps_total` longtext DEFAULT NULL,
    `maps_successful` longtext DEFAULT NULL,
    `render_code` int(11) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- Dumping structure for table ss13_webmap.job_log
CREATE TABLE IF NOT EXISTS `job_log` (
    `job_id` int(11) NOT NULL AUTO_INCREMENT,
    `success` int(11) NOT NULL,
    `start_time` timestamp NULL DEFAULT NULL,
    `end_time` timestamp NOT NULL DEFAULT current_timestamp(),
    `job_log` longtext NOT NULL,
    `codebases_processed` longtext DEFAULT NULL,
    PRIMARY KEY (`job_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

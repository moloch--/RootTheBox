/* SQL updates to an existing RTB instance */

/* 0.7.0 -> 2.0 */

ALTER TABLE `rootthebox`.`flag` 
ADD COLUMN `_case_sensitive` TINYINT(1) NULL DEFAULT 1 AFTER `_type`;
ALTER TABLE `rootthebox`.`flag` 
ADD COLUMN `lock_id` INT(11) NULL DEFAULT NULL AFTER `box_id`,
ADD INDEX `lock_id` (`lock_id` ASC);
ALTER TABLE `rootthebox`.`flag` 
ADD CONSTRAINT `flag_ibfk_2`
  FOREIGN KEY (`lock_id`)
  REFERENCES `rootthebox`.`flag` (`id`)
  ON DELETE SET NULL
  ON UPDATE CASCADE;

ALTER TABLE `rootthebox`.`user` 
ADD COLUMN `_name` VARCHAR(64) NULL DEFAULT '' AFTER `_handle`;

ALTER TABLE `rootthebox`.`hint` 
ADD COLUMN `flag_id` INT(11) NULL AFTER `box_id`;
ALTER TABLE `rootthebox`.`hint` 
ADD INDEX `flag_id` (`flag_id` ASC);
ALTER TABLE `rootthebox`.`hint` 
DROP FOREIGN KEY `hint_ibfk_1`;
ALTER TABLE `rootthebox`.`hint` 
CHANGE COLUMN `box_id` `box_id` INT(11) NULL ;
ALTER TABLE `rootthebox`.`hint` 
ADD CONSTRAINT `hint_ibfk_1`
  FOREIGN KEY (`box_id`)
  REFERENCES `rootthebox`.`box` (`id`);
ALTER TABLE `rootthebox`.`hint` 
ADD CONSTRAINT `fk_hint_1`
  FOREIGN KEY (`flag_id`)
  REFERENCES `rootthebox`.`flag` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

CREATE TABLE `penalty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `team_id` int(11) NOT NULL,
  `flag_id` int(11) NOT NULL,
  `_token` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `team_id` (`team_id`),
  KEY `flag_id` (`flag_id`),
  CONSTRAINT `penalty_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`),
  CONSTRAINT `penalty_ibfk_2` FOREIGN KEY (`flag_id`) REFERENCES `flag` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

ALTER TABLE `rootthebox`.`game_level` 
ADD COLUMN `_type` VARCHAR(10) NOT NULL DEFAULT 'buyout' AFTER `_buyout`;

ALTER TABLE `rootthebox`.`game_level` 
ADD COLUMN `_reward` int(11) NOT NULL DEFAULT '0';

CREATE TABLE `category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `uuid` varchar(36) NOT NULL,
  `_category` varchar(24) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `_category` (`_category`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

ALTER TABLE `rootthebox`.`box` 
ADD COLUMN `category_id` INT(11) NULL DEFAULT NULL AFTER `corporation_id`,
ADD INDEX `category_id` (`category_id` ASC);
ALTER TABLE `rootthebox`.`box` 
ADD CONSTRAINT `box_ibfk_3`
  FOREIGN KEY (`category_id`)
  REFERENCES `rootthebox`.`category` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
  
CREATE TABLE `flag_choice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `uuid` varchar(36) NOT NULL,
  `flag_id` int(11) NOT NULL,
  `_choice` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `flag_id` (`flag_id`),
  CONSTRAINT `flag_choice_ibfk_1` FOREIGN KEY (`flag_id`) REFERENCES `flag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `rootthebox`.`hint` 
CHANGE COLUMN `_description` `_description` VARCHAR(512) NOT NULL ;

/* 2.0 -> 2.1 */

ALTER TABLE `rootthebox`.`team` 
ADD COLUMN `code` VARCHAR(16) NULL DEFAULT NULL AFTER `money`;

ALTER TABLE `rootthebox`.`user` 
ADD COLUMN `money` INT(11) NOT NULL DEFAULT 0 AFTER `algorithm`;

ALTER TABLE `rootthebox`.`game_level` 
ADD COLUMN `_name` VARCHAR(32) NULL DEFAULT NULL AFTER `_reward`;

/* 2.1 -> 2.2 */
ALTER TABLE `rootthebox`.`box` 
ADD COLUMN `flag_submission_type` enum('CLASSIC','SINGLE_SUBMISSION_BOX') DEFAULT 'CLASSIC' AFTER `garbage`;

/* increased hint description field*/
ALTER TABLE `rootthebox`.`hint` 
CHANGE COLUMN `_description` `_description` VARCHAR(1024) NOT NULL ;



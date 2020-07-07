--
-- Database: `kitos`
--
CREATE DATABASE `kitos` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `kitos`;


-- CREATE USER
CREATE USER 'kitos'@'localhost' IDENTIFIED BY 'kitos';
-- GRANT PRIVILEGES ON kitos DATABASE
GRANT ALL PRIVILEGES ON kitos.* TO 'kitos'@'localhost';
-- SAVE THE CHANGES;
FLUSH PRIVILEGES;
-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `cached_data`
--

CREATE TABLE `cached_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kitosID` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `UUID` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `SupplierName` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `Name` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `LocalName` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `Description` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `Url` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `KleName` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `Note` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `BusinessType` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `SystemOwner_name` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `SystemOwner_email` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `OperationalResponsible_name` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `OperationalResponsible_email` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `ContactPerson_name` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `ContactPerson_email` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `ResponsibleOrganizationalUnit` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `TestResponsible_name` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `TestResponsible_email` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `DataLevel` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `DataHandlerAgreement` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `BusinessCritical` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `NoteUsage` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `UsedBy` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `DataHandlerSupplierCvr` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `DataHandlerSupplierName` text CHARACTER SET utf8 COLLATE utf8_danish_ci,
  `TimeOfImport` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `id` (`id`),
  FULLTEXT KEY `Name` (`Name`,`Description`),
  FULLTEXT KEY `Name_2` (`Name`,`LocalName`,`SupplierName`,`Description`,`KleName`,`BusinessType`,`SystemOwner_name`,`SystemOwner_email`,`ContactPerson_name`,`ContactPerson_email`,`ResponsibleOrganizationalUnit`)
) ENGINE=InnoDB AUTO_INCREMENT=413 DEFAULT CHARSET=utf8 COLLATE=utf8_danish_ci;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `usagelog`
--

CREATE TABLE `usagelog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `d1UserName` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `searchString` text CHARACTER SET utf8 COLLATE utf8_danish_ci NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2102 DEFAULT CHARSET=utf8 COLLATE=utf8_danish_ci;
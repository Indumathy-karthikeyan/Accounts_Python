-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: accounts
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `Code` varchar(4) NOT NULL,
  `Description` varchar(50) DEFAULT NULL,
  `PhoneNo` varchar(14) DEFAULT NULL,
  `GstNo` varchar(12) DEFAULT NULL,
  `openbal` decimal(12,2) DEFAULT NULL,
  `BalType` varchar(1) DEFAULT NULL,
  `Year` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `Code` varchar(4) DEFAULT NULL,
  `Description` varchar(50) DEFAULT NULL,
  `Taxable` varchar(1) DEFAULT NULL,
  `HSNCode` varchar(20) DEFAULT NULL,
  `QtyUnit` varchar(5) DEFAULT NULL,
  `QtyToRec` varchar(1) DEFAULT NULL,
  `ytopqty` decimal(12,2) DEFAULT NULL,
  `Year` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `entries`
--

DROP TABLE IF EXISTS `entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entries` (
  `EntryNo` int DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Code` varchar(4) DEFAULT NULL,
  `Narration` varchar(50) DEFAULT NULL,
  `Type` varchar(1) DEFAULT NULL,
  `TransType` varchar(1) DEFAULT NULL,
  `Amount` decimal(12,2) DEFAULT NULL,
  `Year` varchar(10) DEFAULT NULL,
  `Quantity` float DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `transaction`
--

DROP TABLE IF EXISTS `transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction` (
  `EntryNo` int DEFAULT NULL,
  `billno` varchar(8) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `code` varchar(100) DEFAULT NULL,
  `Narration` varchar(100) DEFAULT '',
  `Type` varchar(1) DEFAULT NULL,
  `Rate` float DEFAULT '0',
  `RateType` varchar(4) DEFAULT NULL,
  `Quantity` float DEFAULT '0',
  `Wt` float DEFAULT '0',
  `Amount` decimal(12,2) DEFAULT NULL,
  `Cancelled` varchar(1) DEFAULT 'N',
  `Year` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `narration`
--

DROP TABLE IF EXISTS `narration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `narration` (
  `code` varchar(2) DEFAULT NULL,
  `Description` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `gst`
--

DROP TABLE IF EXISTS `gst`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gst` (
  `StDate` date DEFAULT NULL,
  `IGST` decimal(5,2) DEFAULT NULL,
  `CGST` decimal(5,2) DEFAULT NULL,
  `SGST` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-14 12:54:04

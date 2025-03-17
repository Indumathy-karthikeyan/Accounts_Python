CREATE DATABASE `accounts`

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
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
CREATE TABLE `narration` (
  `code` varchar(2) DEFAULT NULL,
  `Description` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `gst`
--

DROP TABLE IF EXISTS `gst`;
CREATE TABLE `gst` (
  `StDate` date DEFAULT NULL,
  `IGST` decimal(5,2) DEFAULT NULL,
  `CGST` decimal(5,2) DEFAULT NULL,
  `SGST` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

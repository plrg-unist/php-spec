-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 08, 2022 at 07:25 AM
-- Server version: 10.4.19-MariaDB
-- PHP Version: 8.0.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hocms_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `category_list`
--

CREATE TABLE `category_list` (
  `id` int(30) NOT NULL,
  `name` text NOT NULL,
  `description` text NOT NULL,
  `fee` double NOT NULL DEFAULT 0,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `delete_flag` tinyint(1) NOT NULL DEFAULT 0,
  `date_created` datetime NOT NULL DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `category_list`
--

INSERT INTO `category_list` (`id`, `name`, `description`, `fee`, `status`, `delete_flag`, `date_created`, `date_updated`) VALUES
(1, 'Maintenance', 'Collection for maintenance', 200, 1, 0, '2022-02-08 09:19:39', '2022-02-08 09:29:19'),
(2, 'Security', 'Collection for Security', 200, 1, 0, '2022-02-08 09:20:18', '2022-02-08 09:29:38'),
(3, 'Collection 101', 'Sample Collection only', 100, 1, 0, '2022-02-08 09:21:26', '2022-02-08 09:32:17'),
(4, 'Collection 102', 'Sample Collection 102', 100, 1, 0, '2022-02-08 09:21:43', '2022-02-08 09:27:21'),
(5, 'Reserve Fund', 'This is a sample Reserve Fund', 50, 1, 0, '2022-02-08 09:22:31', '2022-02-08 09:29:27');

-- --------------------------------------------------------

--
-- Table structure for table `collection_items`
--

CREATE TABLE `collection_items` (
  `collection_id` int(30) NOT NULL,
  `category_id` int(30) NOT NULL,
  `fee` double NOT NULL DEFAULT 0,
  `date_added` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `collection_items`
--

INSERT INTO `collection_items` (`collection_id`, `category_id`, `fee`, `date_added`) VALUES
(2, 3, 100, '2022-02-08 11:52:33'),
(2, 4, 100, '2022-02-08 11:52:33'),
(2, 1, 200, '2022-02-08 11:52:33'),
(2, 5, 50, '2022-02-08 11:52:33'),
(2, 2, 200, '2022-02-08 11:52:33'),
(1, 3, 100, '2022-02-08 11:58:58'),
(1, 4, 100, '2022-02-08 11:58:58'),
(1, 1, 200, '2022-02-08 11:58:58'),
(1, 2, 200, '2022-02-08 11:58:58'),
(3, 3, 100, '2022-02-08 11:59:32'),
(3, 4, 100, '2022-02-08 11:59:32'),
(3, 1, 200, '2022-02-08 11:59:32'),
(3, 2, 200, '2022-02-08 11:59:32'),
(4, 3, 100, '2022-02-08 13:23:26'),
(4, 4, 100, '2022-02-08 13:23:26'),
(4, 1, 200, '2022-02-08 13:23:26'),
(4, 5, 50, '2022-02-08 13:23:26'),
(4, 2, 200, '2022-02-08 13:23:26');

-- --------------------------------------------------------

--
-- Table structure for table `collection_list`
--

CREATE TABLE `collection_list` (
  `id` int(30) NOT NULL,
  `code` varchar(100) NOT NULL,
  `member_id` int(30) NOT NULL,
  `total_amount` double NOT NULL DEFAULT 0,
  `date_collected` date NOT NULL,
  `collected_by` text NOT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `collection_list`
--

INSERT INTO `collection_list` (`id`, `code`, `member_id`, `total_amount`, `date_collected`, `collected_by`, `date_created`, `date_updated`) VALUES
(1, '202202-00001', 1, 600, '2022-02-08', 'Sample Collector', '2022-02-08 11:47:30', '2022-02-08 11:58:58'),
(2, '202202-00002', 1, 650, '2022-01-06', 'Sample Collector', '2022-02-08 11:52:33', NULL),
(3, '202202-00003', 1, 600, '2021-12-01', 'Sample Collector', '2022-02-08 11:59:32', NULL),
(4, '202202-00004', 2, 650, '2021-12-01', 'Mike Williams', '2022-02-08 13:22:55', '2022-02-08 13:23:26');

-- --------------------------------------------------------

--
-- Table structure for table `member_list`
--

CREATE TABLE `member_list` (
  `id` int(30) NOT NULL,
  `firstname` text NOT NULL,
  `middlename` text DEFAULT NULL,
  `lastname` text NOT NULL,
  `gender` text NOT NULL,
  `contact` text NOT NULL,
  `lot` text NOT NULL,
  `block` text NOT NULL,
  `phase_id` int(30) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `delete_flag` tinyint(1) NOT NULL DEFAULT 0,
  `date_created` datetime NOT NULL DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `member_list`
--

INSERT INTO `member_list` (`id`, `firstname`, `middlename`, `lastname`, `gender`, `contact`, `lot`, `block`, `phase_id`, `status`, `delete_flag`, `date_created`, `date_updated`) VALUES
(1, 'Mark', 'D', 'Cooper', 'Male', '09123456789', '1', '1', 1, 1, 0, '2022-02-08 10:14:45', NULL),
(2, 'Samantha Jane', 'C', 'Anthony', 'Female', '09456789123', '2', '1', 1, 1, 0, '2022-02-08 13:22:35', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `phase_list`
--

CREATE TABLE `phase_list` (
  `id` int(30) NOT NULL,
  `name` text NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `delete_flag` tinyint(1) NOT NULL DEFAULT 0,
  `date_created` datetime NOT NULL DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `phase_list`
--

INSERT INTO `phase_list` (`id`, `name`, `status`, `delete_flag`, `date_created`, `date_updated`) VALUES
(1, 'Phase 1', 1, 0, '2022-02-08 10:02:52', NULL),
(2, 'Phase 2', 1, 0, '2022-02-08 10:02:56', NULL),
(3, 'Phase 3', 1, 0, '2022-02-08 10:03:02', NULL),
(4, 'Phase 4', 1, 0, '2022-02-08 10:03:06', NULL),
(5, 'Phase 5', 0, 1, '2022-02-08 10:03:20', '2022-02-08 10:03:25');

-- --------------------------------------------------------

--
-- Table structure for table `system_info`
--

CREATE TABLE `system_info` (
  `id` int(30) NOT NULL,
  `meta_field` text NOT NULL,
  `meta_value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `system_info`
--

INSERT INTO `system_info` (`id`, `meta_field`, `meta_value`) VALUES
(1, 'name', 'Home Owners Collection Management System'),
(6, 'short_name', 'HOCMS  - PHP'),
(11, 'logo', 'uploads/1644282780_logo.png'),
(13, 'user_avatar', 'uploads/user_avatar.jpg'),
(14, 'cover', 'uploads/1644282780_wallpaper.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(50) NOT NULL,
  `firstname` varchar(250) NOT NULL,
  `lastname` varchar(250) NOT NULL,
  `username` text NOT NULL,
  `password` text NOT NULL,
  `avatar` text DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `type` tinyint(1) NOT NULL DEFAULT 0,
  `date_added` datetime NOT NULL DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `firstname`, `lastname`, `username`, `password`, `avatar`, `last_login`, `type`, `date_added`, `date_updated`) VALUES
(1, 'Adminstrator', 'Admin', 'admin', '0192023a7bbd73250516f069df18b500', 'uploads/1624240500_avatar.png', NULL, 1, '2021-01-20 14:02:37', '2021-06-21 09:55:07'),
(7, 'Claire', 'Blake', 'cblake', '4744ddea876b11dcb1d169fadf494418', 'uploads/1644301020_avatar_2.png', NULL, 2, '2022-02-08 14:17:40', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `category_list`
--
ALTER TABLE `category_list`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `collection_items`
--
ALTER TABLE `collection_items`
  ADD KEY `collection_id` (`collection_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `collection_list`
--
ALTER TABLE `collection_list`
  ADD PRIMARY KEY (`id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `member_list`
--
ALTER TABLE `member_list`
  ADD PRIMARY KEY (`id`),
  ADD KEY `phase_id` (`phase_id`);

--
-- Indexes for table `phase_list`
--
ALTER TABLE `phase_list`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `system_info`
--
ALTER TABLE `system_info`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `category_list`
--
ALTER TABLE `category_list`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `collection_list`
--
ALTER TABLE `collection_list`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `member_list`
--
ALTER TABLE `member_list`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `phase_list`
--
ALTER TABLE `phase_list`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `system_info`
--
ALTER TABLE `system_info`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `collection_items`
--
ALTER TABLE `collection_items`
  ADD CONSTRAINT `collection_items_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category_list` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collection_items_ibfk_2` FOREIGN KEY (`collection_id`) REFERENCES `collection_list` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `collection_list`
--
ALTER TABLE `collection_list`
  ADD CONSTRAINT `collection_list_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member_list` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `member_list`
--
ALTER TABLE `member_list`
  ADD CONSTRAINT `member_list_ibfk_1` FOREIGN KEY (`phase_id`) REFERENCES `phase_list` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

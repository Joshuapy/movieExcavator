// 命令行交互
// joshua
// 2023.9.21

package main

import (
	"flag"
	"fmt"
	"moviecli/DBdriver"
	"os"
)

func showDownloadingMovies(isShow bool) {
	if isShow {
		fmt.Println("=== 下载中的电影 ===")
		DBdriver.ShowDownloadingMovies()
	}
}

func showUnlikedMovies(limit int) {
	if limit > 0 {
		fmt.Println("=== 标记忽略 ===")
		DBdriver.ShowUnlinkedMovies(limit)
	}
}

func showDoneMovies(limit int) {
	if limit > 0 {
		fmt.Println("=== 下载完成 ===")
		DBdriver.ShowDoneMovies(limit)
	}
}

func setStatus(hashes []string, status int) {
	L := 5
	if n := len(hashes); n > L || n < 1 {
		fmt.Printf("一次至少一个或最多设置%d个!\n", L)
		os.Exit(0)
	}
	if status > 4 {
		fmt.Printf("dest_status 取值范围为 0~4, 输入: %d\n", status)
		os.Exit(0)
	}
	DBdriver.SetStatus(hashes, status)
}

func main() {
	// 子命令 show
	showCmd := flag.NewFlagSet("show", flag.ExitOnError)
	var isShowDownloading bool
	var limit int
	var showDoneBylimit int
	showCmd.BoolVar(&isShowDownloading, "d", false, "Is show all downloading movies")
	showCmd.IntVar(&limit, "i", 0, "show the unliked movies with last [n] rows order by create_time")
	showCmd.IntVar(&showDoneBylimit, "w", 0, "show the downloaded movies with last [n] rows order by create_time")

	// 子命令 reset
	resetCmd := flag.NewFlagSet("reset", flag.ExitOnError)
	var dest_status int
	resetCmd.IntVar(&dest_status, "dst", 2, "reset the status to [dst] with special hash of movie, default 1 (1 unlike, 2 like, 3 downloading, 4 done)")

	if len(os.Args) < 2 {
		DBdriver.QueryStatusCount()
		os.Exit(0)
	}

	switch os.Args[1] {
	case "show":
		showCmd.Parse(os.Args[2:])
		DBdriver.QueryStatusCount()
		// -d
		showDownloadingMovies(isShowDownloading)
		// -i
		showUnlikedMovies(limit)
		// -w
		showDoneMovies(showDoneBylimit)
	case "reset":
		resetCmd.Parse(os.Args[2:])
		setStatus(resetCmd.Args(), dest_status)
		// reset status
	case "-h", "--help":
		showCmd.Usage()
		resetCmd.Usage()
	default:
		fmt.Println("Unknow cmd:", os.Args[1])
		showCmd.Usage()
		resetCmd.Usage()
	}
}

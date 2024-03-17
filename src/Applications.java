
import javax.swing.*;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.util.*;

public class Applications {
   
    public static Map<String, FileLock> fileLocks = new HashMap<>();

    public static ArrayList<String> AbsoluteFinder(){
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Choose a file");
        ArrayList<String> files = new ArrayList<>();

        while (true) {
            int returnValue = fileChooser.showOpenDialog(null);

            if (returnValue == JFileChooser.APPROVE_OPTION) {
                File selectedFile = fileChooser.getSelectedFile();
                String absolutePath = selectedFile.getAbsolutePath();
                files.add(absolutePath);
                System.out.println("Selected file: " + absolutePath);
            }
            else {
                System.out.println("Selection Done");
                break; // Break out of the loop when the user cancels
            }
        }
        removeDuplicates(files);
        return files;
    }
    public static void removeDuplicates(ArrayList<String> list) {
        Set<String> set = new HashSet<>();
        List<String> uniqueList = new ArrayList<>();

        for (String str : list) {
            if (!set.contains(str)) {
                set.add(str);
                uniqueList.add(str);
            }
        }

        list.clear(); // Clear the original list

        // Update the original list with unique elements
        list.addAll(uniqueList);
    }
    public static boolean isEmpty(String[] array){
        return array.length==0;
    }

    static void AppLocker(String filePath) {
        try {
            File file = new File(filePath);
            RandomAccessFile randomAccessFile = new RandomAccessFile(file, "rw");
            FileChannel fileChannel = randomAccessFile.getChannel();
            FileLock lock = fileChannel.lock(); // Locking the file
            fileLocks.put(filePath, lock);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    static void UnlockApplications(String[] array){
        for (String string : array){
            System.out.println("UnLocking: " + string);
            Applications.AppUnlocker(string);
        }
    }
    static void LockApplications(String[] array){
        for (String string : array) {
            System.out.println("Locking: " + string);
            Applications.AppLocker(string);
        }
    }
    static void AppUnlocker(String filePath) {
        FileLock lock = fileLocks.get(filePath);
        if (lock != null && lock.isValid()) {
            try {
                lock.release(); // Releasing the lock
                fileLocks.remove(filePath);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
